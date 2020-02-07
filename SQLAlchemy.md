start: `sudo -u postgres psql`

# Grammer

1. foreign key 

   ```sql
   create table SelectCourse(
       studentId Integer,courseId Integer, grade Integer, 
       foreign key (studentId) references student (studentId),
       foreign key (courseId) references course (courseId)
   );
   ```

# Principle

1. Python class can be mapped to `Table` using `mapper()` function

2. [`commit()`](https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session.commit) flushes the remaining changes to the database, and commits the transaction.

3. roll back changes

   `session.rollback()`

4. [`scalar()`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.scalar) invokes the [`one()`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.one) method, and upon success returns the first column of the row:

   ```python
   query = session.query(User.id).filter(User.name == 'ed').order_by(User.id)
   query.scalar()
   # output:
   # 1
   ```

   ​

5. A [`Query`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query) object is created using the [`query()`](https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session.query) method on [`Session`](https://docs.sqlalchemy.org/en/13/orm/session_api.html#sqlalchemy.orm.session.Session).

   ```python
   for instance in session.query(User).order_by(User.id):
       print(instance.name, instance.fullname)# the list of `User`(class) objects present is returned
   ```

6. [`Query`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query) includes a convenience method for counting called [`count()`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.count): determine how many rows the SQL statement would return:

   ```python
   session.query(User).filter(User.name.like('%ed')).count()
   ```

   specify the “count” function directly using the expression `func.count()`: -- # treasures

   ```python
   from sqlalchemy import func
   session.query(func.count(User.name), User.name).group_by(User.name).all()
   [(1, u'ed'), (1, u'fred'), (1, u'mary'), (1, u'wendy')]
   ```

   ​

# Mistake

1. create a schema before mapping to a class