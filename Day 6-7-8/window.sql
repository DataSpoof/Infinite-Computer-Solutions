
-- Create the employee table
CREATE TABLE employ (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE
);


INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (1, 'John', 'Doe', 'HR', 55000.00, TO_DATE('2021-06-15', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (2, 'Jane', 'Smith', 'Finance', 72000.00, TO_DATE('2020-03-10', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (3, 'Michael', 'Johnson', 'IT', 85000.00, TO_DATE('2019-07-22', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (4, 'Emily', 'Davis', 'Marketing', 63000.00, TO_DATE('2021-11-01', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (5, 'David', 'Wilson', 'Operations', 67000.00, TO_DATE('2022-01-15', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (6, 'Emma', 'Brown', 'Sales', 59000.00, TO_DATE('2020-09-20', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (7, 'Olivia', 'Martinez', 'HR', 53000.00, TO_DATE('2019-12-12', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (8, 'James', 'Garcia', 'Finance', 75000.00, TO_DATE('2021-05-08', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (9, 'Isabella', 'Rodriguez', 'IT', 90000.00, TO_DATE('2018-04-05', 'YYYY-MM-DD'));

INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (10, 'William', 'Miller', 'Marketing', 61000.00, TO_DATE('2022-06-30', 'YYYY-MM-DD'));


INSERT INTO employ (employee_id, first_name, last_name, department, salary, hire_date)
VALUES (11, 'Will', 'Miller', 'Marketing', 61000.00, TO_DATE('2022-06-30', 'YYYY-MM-DD'));


-- Commit the transaction
COMMIT;

select * from employ;

SELECT employee_id, first_name, last_name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM employ;

SELECT employee_id, first_name, last_name, salary,department,
       ROW_NUMBER() OVER (partition by department ORDER BY salary DESC) AS row_num
FROM employ;






SELECT employee_id, first_name, last_name, salary,
       RANK() OVER (ORDER BY salary DESC) AS rank
FROM employ;


SELECT employee_id, first_name, last_name, salary,
       RANK() OVER (partition by department ORDER BY salary DESC) AS rank
FROM employ;



SELECT employee_id, first_name, last_name, salary,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employ;

drop table employ;

SELECT employee_id, first_name, last_name, salary,
       NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employ;


SELECT employee_id, first_name, last_name, salary,
       LAG(salary, 2, 0) OVER (ORDER BY salary DESC) AS prev_salary
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       LEAD(salary, 1, 0) OVER (ORDER BY salary DESC) AS next_salary
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       SUM(salary) OVER (ORDER BY salary DESC) AS running_total
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       FIRST_VALUE(salary) OVER (ORDER BY salary DESC) AS highest_salary
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       LAST_VALUE(salary) OVER (ORDER BY salary DESC 
       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_salary
FROM employ;

SELECT employee_id, first_name, last_name, department, salary,
       MAX(salary) OVER (PARTITION BY department) AS max_salary_in_dept
FROM employ;

SELECT employee_id, first_name, last_name, department, salary,
       MIN(salary) OVER (PARTITION BY department) AS min_salary_in_dept
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       CUME_DIST() OVER (ORDER BY salary DESC) AS cumulative_distribution
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       PERCENT_RANK() OVER (ORDER BY salary DESC) AS percent_rank
FROM employ;

SELECT employee_id, first_name, last_name, salary,
       MEDIAN(salary) OVER () AS median_salary
FROM employ;

-- view
create view abcd as 
select employee_id,first_name
from employ;

select * from abcd;

drop view abcd;

create index idx_salary on employ(salary);
drop index idx_salary;

select * from employ;
