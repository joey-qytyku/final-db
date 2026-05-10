'''

There are 8 tables is collegedb.

acats:
    The assignment categories (HW, Lab, etc.)
    ( acID serial primary key, type varchar(30))

stu:
    The students table.

    ( stID serial primary key, name varchar(80), enrolled_date varchar(10))

cor:
    Courses table.
    (
        coID SERIAL ,
        name VARCHAR(30)
    )

cla:
    Classes are instances of courses.
    (
        clID        SERIAL PRIMARY KEY,
        coID        SERIAL REFERENCES cor(coID) NOT NULL
        startTime   VARCHAR(7)
    )

asi:
    Assignment table for all courses

    (
        asID        serial PRIMARY KEY,
        coID        SERIAL REFERENCES cor(coID),
        acID        SERIAL REFERENCES acats(acID)
        name        VARCHAR(60) NOT NULL,
        pointval    INT NOT NULL
    )

gra:
    Grades table for all classes. Grade can be NULL for not graded yet
    and is a percentage in [0.0, 1.0]
    (
        grID    serial primary key,
        asID    serial references asi(asID) NOT NULL,
        grade   NUMERIC
    )

enr:
    Enrollments.
    (
        enID    SERIAL PRIMARY KEY,
        stID    SERIAL REFERENCES stu(stID) NOT NULL, -- Student enrolled
        clID    SERIAL REFERENCES cla(clID) NOT NULL
    )

att:
    Attendence records for all classes. A null date indicates an absense.

    (
        atID serial primary key,
        stID serial references stu(stID) NOT NULL,
        clID serial references cla(clID) NOT NULL
        date varchar(10)
    )

'''
from datetime import datetime, timedelta
import random

days_seq = 1

# Generates a sequential date which makes sense and in the form:
# "yyyy-mm-dd"
# Must use zero padding so that it can be sorted.
#
# This format ensures proper sorting
#

def gen_seq_date() -> str:
    global days_seq
    date = datetime(2026, 1, 1) + timedelta(days=days_seq)

    days_seq+=1

    return f"{date.year:04d}-{date.month:02d}-{date.day:02d}"

def gen_rnd_date():
    from random import randint

    y = 2026
    m = randint(1, 12)
    d = randint(1,27)

    return f"{y:04d}-{m:02d}-{d:02d}"

names_file = open("names", "r")

names = set(names_file.readlines())

names_file.close()

# ID is not in here because it is implcit (we dont modify the table so it
# won't matter.)
students = [ (name.removesuffix("\n"), gen_rnd_date()) for name in names ]

assign_types : list[str] = [
    "NONE",
    "HW",
    "LAB",
    "EXAM",
    "FINAL",
    "PROJECT",
    "PRESENTATION"
]

# List of courses, ID is index
courses = [
    "NONE",
    'BIO-433W', 'ARA-111', 'ART-110', 'ART-291W', 'BIO-392', 'ACCT-240',
    'CHEM-207S', 'CHEM-309', 'BE-382D', 'BE-381A', 'CHEM-382D', 'ART-150',
    'BIO-455W', 'BIO-481', 'BCMB-291', 'BIO-433L', 'ARA-101', 'BCMB-351L',
    'CHEM-381D', 'BCMB-491', 'CHEM-315L', 'ANTH-245', 'CHN-311', 'BE-381D',
    'CHEM-340', 'CHEM-291', 'CHEM-107S', 'BCMB-351', 'CHEM-207', 'BCMB-381D',
    'ART-130', 'CHEM-108', 'CHN-101', 'CHEM-401', 'CHEM-107', 'CHN-211',
    'ART-208', 'BIO-391', 'BCMB-382D', 'BCMB-391', 'BIO-101L', 'ART-233',
    'BCMB-382A', 'CHEM-107LQ', 'ANSO-200', 'CHEM-208L', 'ART-308', 'CHEM-400',
    'BE-382A', 'CHEM-347', 'ART-101', 'CHEM-491W', 'CIE-100', 'CHEM-309L',
    'BIO-491', 'CHEM-391', 'CHEM-108L', 'BCMB-381A', 'CHEM-207L', 'BCMB-493',
    'CHEM-208', 'CHN-312', 'CIE-150', 'ART-105', 'BIO-485', 'ANTH-100',
    'CHEM-208S', 'CHN-111', 'ACCT-140', 'ART-310', 'CHEM-315', 'BCMB-433W',
    'ARA-320', 'ART-210', 'BE-492W', 'ANTH-230'
]

# coID, startTime
classes : list[tuple[int, str]] = [ (0, "NONE") ]

# stID, clID
enrollments : list[tuple[int, int]] = [ (0,0) ]

# coID, name, pointval
assignments : list[tuple[int, int, str, int]] = [ (0, 0, "NONE", 0) ]

grades : list[ tuple[int, int, int, float] ] = [ (0,0,0)]

# stID, clID, date
attendance : list[tuple[int, int, str]] = [ (0,0,"") ]

def create_classes_and_enr():
    start_times : list[str] = [
        "08:00AM",
        "08:30AM",
        "09:30AM",
        "10:00AM",
        "01:30PM",
        "03:00PM"
    ]

    clID = 1

    # In Ursinus, each class has between 2-4 sections.
    for coID in range(1, len(courses)):
        for _ in range(random.randint(2,4)):
            # Randomly select one of several time slots.
            startTime = random.choice(start_times)
            classes.append((coID, startTime))
            clID += 1

    # Assign every student to 4 random classes.
    #! FLAG: Actually go do that! This is not 4 classes?
    #! They are all enrolled in just one RN.
    for stID in range(1, len(students)):
        for x in range(4):
            clID = random.randint(1, len(classes)-1)
            enrollments.append((stID, clID))

# In our data set the names of assignments will be the first word of the
# course title, the type, and the number because there are several of each type.
#
def create_assignments():
    types_nfin = [x for x in assign_types if x != "FINAL"]

    for coID in range(1, len(courses)):
        cname = courses[coID]
        cname = cname[:cname.find("-")]

        for _ in range(25):
            atype = types_nfin[random.randint(1, len(types_nfin)-1)]
            aname = f"{cname} {atype}"
            points = 5 * random.randint(1, 8)

            assignments.append((coID, assign_types.index(atype), aname, points))

        # Add a final assignment
        assignments.append((coID, assign_types.index("FINAL"), "Final", 150))

def create_grades():
    # Look into the class enrollments of each student and give them grades.

    for enID in range(1,len(enrollments)):
        stID = enrollments[enID][0] # ID of of the student
        clID = enrollments[enID][1] # ID of class the student is enrolled into

        print(f"stID:{clID}")
        # Now get the course ID with the class ID
        coID = classes[clID][0]

        # Get the indices (or IDs) or every assignment for this course.

        course_asgs = \
        [ n for n in range(1, len(assignments)) if assignments[n][1] == coID ]

        # Give random grades for these assignments
        for asID in course_asgs:
            percentage : float = random.random()

            grades.append((clID, stID, asID, percentage))

def create_attendance():
    # For our purposes, a 90% attendance rate is used.
    # A null entry is used to represent an absence.
    # The problem with CSV is that it does not have the concept of a NULL
    # and cannot distinguish it from an empty string.
    # This is fine because it can always be substituted with an SQL command.

    SCHOOL_DAYS = 120

    for _ in range(SCHOOL_DAYS):
        # Generate a date for this school day
        date = gen_seq_date()

        # For each student, 90% chance they are present.
        for stID in range(1, len(students)):
            # Get every class that they are enrolled in
            their_classes = \
            [ e[1] for e in enrollments if e[0] == stID]

            # Now have them attend each of these classes at the expected rate

            for clID in their_classes:
                if random.random() <= 0.9:
                    attendance.append((stID, clID, date))
                else:
                    attendance.append((stID, clID, ""))

def print_csv(file_name: str, L: list):
    f = open(file_name, "w")
    i = 1
    for x in L[1:]:
        as_list = [str(n) for n in list(x)]
        f.write(f"{i}," + (','.join(as_list) + '\n'))
        i += 1

    f.close()

create_classes_and_enr()
create_assignments()
create_grades()
create_attendance()

print_csv("enrollments.csv", enrollments)
print_csv("attendance.csv", attendance)

print_csv("students.csv", students)
print_csv("acats.csv",  [(x,) for x in assign_types])
print_csv("assignments.csv",  assignments)

print_csv("courses.csv",  [(x,) for x in courses])
print_csv("classes.csv", classes)
print_csv("grades.csv",  grades)
