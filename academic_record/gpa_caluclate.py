
from decimal import Decimal


def gpa_calculate(written_works, performance_tasks, quarterly_assessments):
    # Define weightage percentages for each assessment type
    WRITTEN_WORKS_WEIGHTAGE = Decimal(written_works['weightage'])
    PERFORMANCE_TASKS_WEIGHTAGE = Decimal(performance_tasks['weightage'])
    QUARTERLY_ASSESSMENTS_WEIGHTAGE = Decimal(
        quarterly_assessments['weightage'])

    """
        written_works = ([(score/total), (score/total), (score/total)] / lenght) * percentage
        performance_task = ([(score/total), (score/total), (score/total)] / lenght) * percentage
        quarterly_assessment = ([(score/total), (score/total), (score/total)] / lenght) * percentage
    """

    # Obtain marks for each assessment type
    written_works_marks = written_works['obtained_marks']
    performance_tasks_marks = performance_tasks['obtained_marks']
    quarterly_assessments_marks = quarterly_assessments['obtained_marks']

    if len(written_works_marks) == 0 or len(performance_tasks_marks) == 0 or len(quarterly_assessments_marks) == 0:
        return 'N/A'

    # Calculate weighted marks for each assessment type
    weighted_written_works_marks = sum(
        written_works_marks) / len(written_works_marks) * WRITTEN_WORKS_WEIGHTAGE
    weighted_performance_tasks_marks = sum(
        performance_tasks_marks) / len(performance_tasks_marks) * PERFORMANCE_TASKS_WEIGHTAGE
    weighted_quarterly_assessments_marks = sum(quarterly_assessments_marks) / len(
        quarterly_assessments_marks) * QUARTERLY_ASSESSMENTS_WEIGHTAGE

    # Sum up total weighted marks
    total_weighted_marks = (weighted_written_works_marks +
                            weighted_performance_tasks_marks +
                            weighted_quarterly_assessments_marks)

    # Sum up total weightage
    total_weightage = (WRITTEN_WORKS_WEIGHTAGE +
                       PERFORMANCE_TASKS_WEIGHTAGE +
                       QUARTERLY_ASSESSMENTS_WEIGHTAGE)

    # Calculate overall grade
    overall_grade = total_weighted_marks / total_weightage * 100

    return str(round(overall_grade, 2))
