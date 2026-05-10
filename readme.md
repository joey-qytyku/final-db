# College Learning Management Example Database

## Overview

The database simulates the LMS of a college about the size of Ursinus. It would be used in real life by migrating the student and course information to newer iterations of the database every semester and creating the rest of the tables with newer information.

All the data was randomly generated using a complex python script (which is included here).

It contains the following tables that make heavy use of foreign keys:
1. Students (`stu`)
	- Name, ID, and date enrolled.
2. Courses (`cor`)
3. Assignments (`asi`)
	- Defined for each course (by their ID).
4. Grades (`gra`)
	- It was my bad decision to use a double precision type to store the grade, which makes some of the queries more complicated than necessary.
	- Points possible NOT stored here.
	- Maps to the student AND the class because classes -> assignments is many to one.
5. Attedance (`att`)
	- Date and class included
	- NULL means not present
6. Classes (`cla`)
	- An "instance" of a course.
	- There are 2-4 for each course, which seems typical in Ursinus.
7. Enrollments (`enr`)
	- A junction table that maps a student to a class
8. Assignment categories (`acat`)
	- Lab, HW, Final, etc.

Dates are stored in the following zero-padded form:
```
YYYY-MM-DD
```

Times of day look like this:
```
hh:mmAM
hh:mmPM
```

The zero padding is necessary because they would not be lexicographically sortable (they are all of the `VARCHAR` type).

## Documentation for functions, procedures, and queries

### Basic queries

#### Get every course taken by a student

```sql
select cor.name from cor
inner join cla on cla.coID = cor.coID
inner join enr on enr.clID = cla.clID
inner join stu on stu.stID = enr.stID
where stu.stID = 1;
```

Returns one column with each course name.

#### Get all courses taken by every student

```sql
select stu.name as "Student", string_agg(cor.name, ', ') as "Course Name" from stu
inner join enr on stu.stID = enr.stID
inner join cla on cla.clID = enr.clID
inner join cor on cla.coID = cor.coID
group by stu.name
order by stu.name asc;
```

This uses `STRING_AGG` which was *not* covered in our course. It concatenates the grouped rows with a string separator, in this case a comma.

Results look something like this:
```
Aaliyah Grant	"ANTH-100, BE-382A, CHEM-381D, ART-101"
Abby Frye		"BIO-433L, BCMB-291, ACCT-140, BCMB-493"
Abigail Haley   "ARA-320, ACCT-140, ART-101, CHEM-108L"
Abner Maldonado	"BE-381A, CHEM-309L, CHEM-108, ART-130"
Abner Robinson	"BCMB-382A, ART-208, CIE-150, CHEM-381D"
	...
```

#### Attendance of each student as percentage `xx.y`

Absences are indicated by a NULL date. We use `COUNT(*)` to get the total attendances possible (for the student, it is an aggregate), and `COUNT(att.date)` for the total attendances.


```sql
select stu.name, CONCAT( CAST(CAST(COUNT(att.date) as DOUBLE PRECISION) / COUNT(*) * 100 as NUMERIC(100,1)), '%') as 'Attendance rate'
from att
inner join stu on stu.stID = att.stID
group by stu.name;
```
A cast to NUMERIC and addition of "%" generates a report with a formatted percentage. The calculation is done in double precision which offers adequate accuracy for the steps taken.

> It is still possible to know the date they were absent, but this requires a much more complex method not covered here.

### Complex queries

Most of these are defined as functions returning tables because they are quite long.

#### Get every assignment and grade for specific student

```sql
create or replace function get_all_student_assignments(s_name varchar(80))
RETURNS table( assign_name varchar,  pts_obtained int, points_total int)
AS $$
BEGIN
	return query (
		with student_id as (select stID from stu where stu.name = s_name)
		select asi.title as assign_name, CAST(gra.grade * asi.points as int) as pts_obtained, asi.points as points_total from gra
		inner join asi on asi.asID = gra.asID
		where gra.stID = (select * from student_id)
	);
END;
$$ LANGUAGE plpgsql;
```

> This is NOT efficient when repeated for multiple students.

#### Rank the grades for each individual assignment for all classes

This uses a CTE and `DENSE_RANK`. It first gets the grades in a more suitable format along with the student and assignment IDs, and does a dense rank while paritioning over the assignment ID (to have local ranks for each assignment).

```sql
create or replace function rank_grades_for_every_assignment()
RETURNS table(
	grade_rank_ bigint,
	asID_ int,
	stID_ int,
	pts_obtained_ int,
	points_total_ int
)
AS $$
BEGIN
RETURN QUERY(
	WITH assign_grades as (
		select	stu.stID as stID,
				stu.name as name,
				asi.asID as asID,
				CAST(gra.grade * asi.points as int) as pts_obtained,
				asi.points as pts_total
		from gra
		inner join stu on stu.stID = gra.stID
		inner join asi on gra.asID = asi.asID
	)
	select dense_rank() over (partition by asID order by pts_obtained desc) as grade_rank,
			asID,
			stID,
			pts_obtained,
			pts_total
	from assign_grades
);
END; $$ LANGUAGE plpgsql;
```

Example use:
```sql
select * from rank_grades_for_every_assignment();
```

#### Calculate GPA for all students and show descending

The GPA is essentially the grade multiplied by 4 in this case.

```sql
WITH assign_grades as (
	select stu.stID as stID, stu.name as name, asi.asID as asID, CAST(gra.grade * asi.points as int) as pts_obtained, asi.points as pts_total
	from gra
	inner join stu on stu.stID = gra.stID
	inner join asi on gra.asID = asi.asID
)
select assign_grades.stID, (SUM(CAST(assign_grades.pts_obtained as DOUBLE PRECISION)) / SUM(assign_grades.pts_total) * 4) as gpa from assign_grades
group by stID order by gpa desc;
```
