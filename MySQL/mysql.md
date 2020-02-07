# ER 图

 PK=主键;NN=非空;UQ=唯一;BIN=二进制流;UN=正整数;AI=自增 

# Mysql

1. ![image-20191119224211843](typora-user-images\image-20191119224211843.png)

   从[Mysql 5.7](https://dev.mysql.com/doc/refman/5.7/en/show-columns.html)文件：

   - 如果键是PRI，则列是主键或多列主键中的列之一。
   - 如果键是UNI，则该列是唯一索引的第一列。(唯一索引允许多个空值，但可以通过检查Null字段来判断该列是否允许空。)
   - 如果键为MUL，则该列是非唯一索引的第一列，其中允许在列中多次出现给定值。

# 安装

1. ```shell
   #shell
   sudo apt-get install mysql-server
   sudo apt install mysql-client
   sudo apt install libmysqlclient-dev
   
   # 以及具体步骤参考:https://www.youtube.com/results?search_query=ubuntu18.04+mysql
   ```

2. ```sql
   --sql shell
   update user set plugin='mysql_native_password' where user='root'; --修改密码
    update mysql.user set authentication_string=PASSWORD('0925')  where user='root'; --设定新密码
    --若报错密码太简单,修改mysql参数配置:https://blog.csdn.net/kuluzs/article/details/51924374
    flush privileges
   --reload the grant tables, 更新系统权限表,防止拒绝访问a
   ```

# 命令行

1. 创建数据库: `create database hunt_game;`
2. 指定数据库:`use hunt_game;`

3. 查看有哪些表: `show tables;`
4. 查看表的详情: `describe table_name;`

# Workbench

1. 生成ER图:  file-->new model-->ctrl+r-->next-->reverse engineering-->finish

   ![image-20191119112836927](typora-user-images\image-20191119112836927.png)

# Pycharm

 https://www.youtube.com/watch?v=cYWiDiIUxQc 

 https://www.youtube.com/watch?v=0yid46tNIDw 

1. ```shell
   pip install pymysql # driver
   ```

2. ```python
   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy
   
   app = Flask(__name__)
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:0925@127.0.0.1:3306/hunt_games' #dialect+driver://username:password@host:port/database
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
   db = SQLAlchemy(app) # the instance of DB
   
   ```

3. 类名的两种取法

   - 小写化后和表名一致
   - 在类中定义`__tablename__=表名`

4. `def __repr__(self)`:  不管直接输出对象还是通过print打印的信息都按我们\__repr__方法中定义的格式进行显示了

   ![image-20191119132018855](typora-user-images\image-20191119132018855.png)

4. `f"string{表达式}"`:[格式化输出] 以f或F修饰符引领的字符串中, 以大括号{}标明被替换的字符串

   ```python
   t = {'name': 'Tuesday'}
   f"The t is {t['name']}.""
   ```

   - 注意引号的使用,字符串内外部引号相同时需要用`\`转义
   - 注意括号: 如果字符串中包含括号, 则需要用双括号包裹它
   - 在表达式中
     - 不能使用反斜杠转义字符
     - 不能出现`#`

5. 传递函数**值**作为参数`default=datetime.utcnow()`

   传递函数作为参数`default=datetime.utcnow`

# SQLAlchemy

 https://docs.sqlalchemy.org/en/13/orm/tutorial.html#adding-and-updating-objects 

1. `table.__table_`: ![image-20191119202427194](typora-user-images\image-20191119202427194.png)

## table

1. ```python
   # wirte this in the .py file
   class Test(db.Model):
       # table name
       # __tablename__='test'
       # table structure
       id = db.Column('id', db.Integer, primary_key=True)
       name = db.Column('name', db.String(20), nullable=False)
       posts = db.relationship('Post', backref='author', lazy=True)
   
       def __repr__(self):
           return f"User({self.id},'{self.name}')"
   ```

   ![image-20191120161744660](typora-user-images\image-20191120161744660.png)
   
2. 插入`db.session.add(object)`等同于insert

   ```python
   user_1 = Test(name='user1')
   user_2 = Test(id=110, name='user2')
   db.session.add(user_1)
   db.session.add(user_2)
   # db.session.add_all([user_1,user_2])
   db.session.commit() #commit transaction
   ```

   - `id`: primary key , user_1 will be assigned a unique ID automatically 
   - ![image-20191120161721566](typora-user-images\image-20191120161721566.png)

3. 查询

   - `.filter()`: .filter(User.name.in**_**(['Edwardo', 'fakeuser']))

     - [`equals`](https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators.__eq__):

       ```
       query.filter(User.name == 'ed')
       ```

     - [`not equals`](https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators.__ne__):

       ```
       query.filter(User.name != 'ed')
       ```

     - [`LIKE`](https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators.like):

       ```python
       query.filter(User.name.like('%ed%'))
       ```

     -  [`IN`](https://docs.sqlalchemy.org/en/13/core/sqlelement.html#sqlalchemy.sql.operators.ColumnOperators.in_): 

       ```python
       query.filter(User.name.in_(['ed', 'wendy', 'jack']))
       # use tuple_() for composite (multi-column) queries
       from sqlalchemy import tuple_
       query.filter(
           tuple_(User.name, User.nickname).\
           in_([('ed', 'edsnickname'), ('wendy', 'windy')])
       )
       ```

    `.limited(1)`

   -  `.all()`,

     Return the results represented by this [`Query`](https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query) as a **list.**

   -  `.first()`,

   `.get(PK ID)`

   `.order_by()`

   `func.count()`:  used to determine how many rows the SQL statement would return.  

   ```python
   # run this in the terminal-python
   db.session.query(Test).all() # return a list
   db.session.query(Test).filter_by(name=='user_1').all()
   # count()
   from sqlalchemy import func
   db.session.query(func.count(User.name), User.name).group_by(User.name).all()
   [[(1, u'ed'),  (1, u'fred')] 
   ```

   ![image-20191119140501892](typora-user-images\image-20191119140501892.png)

   ![image-20191119140433157](typora-user-images\image-20191119140433157.png)

   没有结果则返回`None`

4. 修改

   - SQLalchemy

     第一种方法:

     ```python
     db.query.filter().one().attribute='change'
     db.session.flush()
     ```

     第二种:

     ```python
     db.session.merge(instance)
     ```

     - examines the primary key attributes of the source instance, and attempts to reconcile it with an instance of the same primary key in the session.
     -  If not found locally, it attempts to load the object from the database based on primary key, and
       -  if none can be located, creates a new instance. The state of each attribute on the source instance is then copied to the target instance. The resulting target instance is then returned by the method; the original source instance is left unmodified, and un-associated with the Session if not already.

   - SQL: 

     - 列名` alter table 表名 change column 旧列名 新列名  新列名格式； `

     - 类型`alter table 表名 modify column 列名 新格式; `

     - 默认值

       - 时间类型和函数https://blog.csdn.net/gxy_2016/article/details/53436865

         **MySQL 的日期类型如何设置当前时间为其默认值**？
         答：请使用 timestamp 类型，且 默认值设为 now() 或 current_timestamp() 

   - SQLalchemy

5. 删除`db.session.delete(object)`

   ![image-20191120161619690](typora-user-images\image-20191120161619690.png)

   ```python
   db.session.delete(me)
   db.session.commit()
   ```

6. 回滚`db.session.rollback()`

7. bind key

    https://flask-sqlalchemy.palletsprojects.com/en/2.x/binds/ 

8. 外键:

   - fk_id: 外键别名

   - 创建表时: `constraint fk_id foreign key (fk) references characters(pk) on  delete cascade;`

   - 删除外键:

     ` ALTER TABLE article DROP FOREIGN KEY fk_id `

   - 对已有属性增加外键约束

     ```shell
     alter table table_name 
     add constraint FK_ID foreign key (FK_name) references table_name (PK_name);
     ```

   - 更改外键约束模式

   - 区别

     - 外键和外键约束不同
     -  delete-orphan: 是保证了如果parent被删除, 那么与之关联的外键一定会被删除;

     

9. 索引和字段的增删

   - 字段

     ```python
     # 增加
     ALTER TABLE table_name 
     add field_name field_type;
     # 更改
     alter table table_name 
     change old_field_name new_field_name field_type;
     # 删除
     alter table table_name 
     drop field_name;
     ```

   - 索引

      https://blog.csdn.net/u013063153/article/details/53304325 

     

     

## relationship

1. 1-N: User model: Post model [one user -multiple post]

   ```python
   # add this into User class
   posts = db.relationship('Post',backref='author', lazy=True)
   # while the Post class is defined as
   class Post:...
   
   ```

   `relationship`

   - not a column
   - run a query in the background on post table

   `'Post'`

   - the 'Post' is the same as the class name, to reference the actual Post class(so can have upper case)

   - this will be compared to the reference of table name and the column name

     ```python
     # add this in the Post class
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     # table name: user, column name:id ,so are lower case
     ```

   `backref`: 

   - add another column to the Post model;[ not a actual column]
   - when have a post, can use 'author' attribute to get the user who created the post

   `lazy`:

   - when SQL alchemy loads data from DB

   - True: load data as necessary in one go

     -->use the 'post' attribute to get all posts created by a user

   

# split into files

1.  https://www.youtube.com/watch?v=44PvX0Yv368&t=930s 

   from start to 6:44

   - problem:

     ![img](file:///C:\Users\xiongxiaoji\Documents\Tencent Files\1051011941\Image\C2C\{0604DA38-856E-2A00-6CB5-C8F982F9F5B0}.png) 

   - solution:

     有先后顺序:

     - move the class into model.py:

       - change `from hunt_game import db` to `from __main__ import db`

         防止python再次run flaskblog, 解决报错 can't import User

     - in the flaskblog.py

       - the `__main__` is in this file;

       - move the `from models import User, Posts`  after `db=SQLAlchemy(app)`

         防止python在run models时, 无法 import db

   - addition:
     - `'__main__'`时顶层代码执行的作用域
     -  模块的`__name__`,在通过标准输入、脚本文件或是交互式命令读入的时候会等于 `'__main__'`。 
     - 模块可以通过检查自己的`__name__`,得知是否运行在main作用域中,使得模块作为脚本或者用`python -m`被运行时条件性地执行一些代码, 在被import时不会执行

# lib

1. bcrypt: 

   - get different hash even with same passwd: `bcrypt.generate_password_hash('test').decode('utf-8')`  

     ![image-20191119170251478](typora-user-images\image-20191119170251478.png)

   - check

     ![image-20191119170531665](typora-user-images\image-20191119170531665.png)

   

