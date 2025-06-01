from typing import Dict, Any
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from app.groups.models import Group, GroupCourse
from app.groups.services import exceptions
from app.tasks.queries import CreateOrUpdateCourseUserStatisticsQuery
from app.tasks.models import UserStatistics, TaskItem
from app.tasks.entities import TaskItemStatistics
from app.tasks.enums import TaskItemType
from app.groups.enums import GroupMemberRole
from app.tasks.models import Solution
from django.db.models import Q

UserModel = get_user_model()


class GroupStatisticsService:
    @classmethod
    def get_group_course(cls, group: Group, course_id: int) -> GroupCourse:
        try:
            group_course = group.group_courses.get(course_id=course_id)
        except ObjectDoesNotExist:
            raise exceptions.CourseNotFoundException()
        else:
            teacher_permission = (
                group.user_is_teacher and group_course.statistics_allow_for_teacher()
            )
            learner_permission = (
                group.user_is_learner and group_course.statistics_allow_for_learner()
            )
            if not teacher_permission and not learner_permission:
                raise exceptions.GroupStatisticPermissionError()
            return group_course

    @classmethod
    def get_course_statistics(
        cls,
        group: Group,
        course_id: int,
        user: UserModel
    ) -> Dict[str, Any]:

        """ Формат ответа:
            {
                "tasks_max_points": { "<task_id>": <max_score>, ... },
                "stats": {
                    user_id_1: {
                        taskitem_id_1: {...},
                        ...
                    },
                    ...
                }
            }
        """

        result: Dict[int, Dict[int, TaskItemStatistics]] = {}
        group_course = cls.get_group_course(group=group, course_id=course_id)
        version_hash = group_course.course.get_cache_data()['version_hash']
        user_ids = set(group.learners.only_ids())

        objs = list(
            UserStatistics.objects.filter(
                type_id=course_id,
                type=TaskItemType.COURSE,
                user_id__in=user_ids
            )
        )
        for obj in objs:
            if obj.version_hash != version_hash:
                query = CreateOrUpdateCourseUserStatisticsQuery(
                    user_id=obj.user_id,
                    course_id=course_id,
                    version_hash=version_hash,
                )
                obj = UserStatistics.objects.raw(*query.get_sql())[0]
            user_ids.remove(obj.user_id)
            result[obj.user_id] = obj.data

        # users without statistics
        for user_id in user_ids:
            query = CreateOrUpdateCourseUserStatisticsQuery(
                user_id=user_id,
                course_id=course_id,
                version_hash=version_hash,
            )
            obj = UserStatistics.objects.raw(*query.get_sql())[0]
            result[obj.user_id] = obj.data

        # «task_id → max_score»
        tasks_qs = (
            TaskItem.objects
            .filter(topic__course=group_course.course)
            .values("id", "max_score")
        )
        tasks_max_points = {
            t["id"]: float(t["max_score"]) for t in tasks_qs
        }
        first_solutions = (
            Solution.objects
            .filter(
                task_id__in=list(tasks_max_points.keys()),
                user_id__in=result.keys(),
            )
            .filter(
                Q(score__gt=0) | Q(review_status__in=['ready', 'review'])
            )
            .order_by('user_id', 'task_id', 'id')
            .distinct('user_id', 'task_id')
            .values('user_id', 'task_id', 'time_spent', 'needs_manual_check')
        )

        sol_map = {
            (str(s["user_id"]), str(s["task_id"])): (
                int(s["time_spent"] or 0),
                bool(s["needs_manual_check"])
            )
            for s in first_solutions
        }

        for user_id, tasks in result.items():
            for task_id, cell in tasks.items():
                exec_time, too_fast = sol_map.get((str(user_id), str(task_id)), (0, False))
                cell["execution_time"] = int(exec_time or 0)
                cell["needs_manual_check"] = too_fast

        is_teacher = group.group_members.filter(
            user=user,
            role=GroupMemberRole.TEACHER
        ).exists()

        return {
            "tasks_max_points": tasks_max_points,
            "stats": result,
            "is_teacher": is_teacher,
        }