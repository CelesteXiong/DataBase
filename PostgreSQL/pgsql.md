1. start: `sudo -u postgres psql`







## 设计

1. 高效执行：先形成中间关系，再和满足条件的元组连接形成结果关系 《书P101》

## 语法

### 视图

1. 普通视图（虚拟表）：修改视图会导致基表一起被修改

   ```sql
   create view sub_table as (select ... from ... where ...)	
   ```

   普通视图不存储数据，只有定义，在查询中是转化为对应定义的SQL。

2. 建立物化视图

   ```sql
   create materialized view sub_table as (select ... from ... where ...)
   ```

   刷新时通过关联表上创建相应的log，根据log的SQL同步到物化视图中

### 单表删改

1. 插入

   ```sql
   insert into table_name(column1, c2,...)
   values (value1, value2, ...);
   ```

   or

   ```sql
   insert into table_name
   values (value1, v2,...);
   ```

### 单表查询

1. 消除重复

   - distinct：在列名前添加

2. 比较

   - between a and b（闭区间）
   - 判断空值：is null/ is not null

3. 匹配

   ```sql
   where [not] like '<匹配串>'
   ```

   - 匹配串：
     - 一串字符
     - 通配符%: 任意长度字符串（可以为0）
     - 通配符_: 任意单个字符
     - 数据库字符集为ASCII时需要两个_，为GBK时需要一个
     - escape进行转义

4. 排序

   ```sql
   where ... order by ... asc/desc
   ```

   - 升序：asc
   - 降序： desc
   - 对于空值，一般将空值作为最低序的

5. 聚集函数

   - 只用于`select` 子句和`group by`的 `having`子句

   - ```sql
     count(参数) 参数：*/列名，默认为all 
     sum(参数)
     ```

   - 类似： 

     ```sql
     avg(), max(), min
     ```

   - 遇到控制，除了`count(*)`外，都跳过空值，只处理非空值 [count(*) 是对元组计数，某个元组中的一个或部分列取空值不影响count结果]

6. group by

   - 分组后，聚集函数将作用于每一个组；

   - `where`不用聚集函数作为套件表达式

     错误：

     ```sql
     select avg(grade)
     from sc
     where avg(grade) > 90
     group by sno;
     ```

     正确：

     ```sql
     select avg(grade)
     from sc
     group by sno
     having avg(grade)>90;
     ```


### 多表查询

没太弄懂，多看《书103-111》

1. 嵌套查询：分步

   - 谓词： in， all， any（某一个，不是任意一个）， exists(因为exists只返回真假值，一般select目标列表达式为*)
   - exists：内层为非空，外层的where子句返回真
   - not exists: 内层为空，外层的where返回真
   - 相关子查询：子查询的条件和父查询相关
2. 外连接：
   - from 左表 left outer join 右表 on (约束)

# success

1. book5.4

   ![book5.4](/home/syx/文档/Git/book5.4.png)

2.  book5.6

   ![book5.6](/home/syx/文档/Git/book5.6.png)

3. book 5.7

   ![book5.7](/home/syx/文档/Git/book5.7.png)

4. lab2.9

   ![lab29)](/home/syx/文档/Git/lab2.9.png)

   ​

# mistake

1. like: remember to add '%' or '_'

   `select jname from public.j where j.name like 'Tianjin'`

   change `Tianjin`to:

   `Tianjin%`

2. in: used when query returns more than one rows

   `select * from public.p where p.pno =  (select pno from spj where spj.sno = (select sno from public.s where s.sname = '精益'));`

   chand `=` to:

   `in`

   ​