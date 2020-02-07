# 数据库实验
## 实验一
1、PostgreSQL 安装
[Windows](https://www.yiibai.com/postgresql/install-postgresql.html)
[Linux](https://www.cnblogs.com/freeweb/p/8006639.html)


2、创建数据库和表  
使用SQL语句，完成创建一个数据库，创建关系。

&emsp;1）创建数据库scDB；

&emsp;2）按要求创建四个表：  
&emsp;&emsp;Student(Sno,Sname,Ssex,Sage,Sdept)  
&emsp;&emsp;Course(Cno,Cname,Cpno,Ccredits)  
&emsp;&emsp;SC(Sno,Cno,Grade)

&emsp;3）为属性选择合适的域、合适的主码和外键约束；

3、运行脚本SPJ.sql
```
\i your_Path
```
4、简单单表查询  

&emsp;在SPJ的基础上，完成教材第三章习题5。

## 实验二
掌握SELECT/SELECT DISTINCT/WHERE/AND/OR/ORDER BY/INSERT INTO/UPDATE/DELETE等操作

5、查询操作

  1）在零件表的视图中找出weight < 20 的零件名字(PNAME)  

```sql
select pname from p where weight < 20;
   pname   
-----------
 螺母    
 螺栓    
 螺丝刀   
 螺丝刀   
(4 rows)
```

  2）查询供应商表中城市为北京的供应商姓名(SNAME)  

```sql
select sname from s where city = '北京';
   sname   
-----------
 盛锡    
 东方红   
(2 rows)
```

  3）在零件表中查询平均重量在15以上的零件名字和零件代码（PNO）  

```sql
select pname, pno from p group by (pname, pno) having avg(weight) > 15; 
  pname   | pno 
----------+-----
 凸轮     | P5
 螺栓     | P2
 齿轮     | P6
(3 rows)
```

but no aggregation causing by pno(pno must be added into group by's args because: )

```sql
select pname, pno from p group by (pname) having avg(weight) > 15; 
ERROR:  column "p.pno" must appear in the GROUP BY clause or be used in an aggregate function
LINE 1: select pname, pno from p group by (pname) having avg(weight)...
                      ^
```

  so if we need to output pname and pno, based on the aggredation by pname, use `correlation subquery` :

```sql
select pname, pno from p A where (select avg(B.weight) from p B where B.pname = A.pname) > 15;
  pname   | pno 
----------+-----
 螺栓     | P2
 凸轮     | P5
 齿轮     | P6
(3 rows)
```

let's test:

```sql
--update the tabel p
update p set weight = 30 where pno = 'P4';
select * from p;
 pno |   pname   | color | weight 
-----+-----------+-------+--------
 P1  | 螺母      | 红    |     12
 P2  | 螺栓      | 绿    |     17
 P3  | 螺丝刀    | 蓝    |     14
 P5  | 凸轮      | 蓝    |     40
 P6  | 齿轮      | 红    |     30
 P4  | 螺丝刀    | 红    |     30
(6 rows)
```

```sql
select pname, pno from p A where (select avg(B.weight) from p B where B.pname = A.pname) > 15;
   pname   | pno 
-----------+-----
 螺栓      | P2
 螺丝刀    | P3
 凸轮      | P5
 齿轮      | P6
 螺丝刀    | P4
(5 rows)
-- the output is right: 2 螺丝刀 should be printed;
```

```sql
select pname, pno from p group by (pname, pno) having avg(weight) >15;
   pname   | pno 
-----------+-----
 凸轮      | P5
 螺栓      | P2
 螺丝刀    | P4
 齿轮      | P6
(4 rows)
-- output is wrong for no aggregation is applied, only 1 螺丝刀 is printed;
```

4）查询全体供应商的姓名（SNAME）和状态(STATUS)  

```sql
select sname, status from s;
   sname   | status 
-----------+--------
 精益      | 20
 盛锡      | 10
 东方红    | 30
 丰泰盛    | 20
 为民      | 30
(5 rows)
```

  5）查询所有weight在13到20岁（含13和20）的零件代码（PNO）、零件名（PNAME）和颜色(COLOR)  

```sql
select pno, pname, color from p where weight between 13 and 20;
 pno |   pname   | color 
-----+-----------+-------
 P2  | 螺栓      | 绿 
 P3  | 螺丝刀    | 蓝 
(2 rows)
```

  6）查询所有“螺”开头的的零件代码（PNO）和零件名（PNAME）  

```sql
select pno, pname from p where pname like '螺%';
 pno |   pname   
-----+-----------
 P1  | 螺母    
 P2  | 螺栓    
 P3  | 螺丝刀   
 P4  | 螺丝刀   
(4 rows)
```

  7）查询所有零件的平均重量  

```sql
select avg(weight) from p;
         avg         
---------------------
 21.1666666666666667
(1 row)
```

  8）查询同在“天津”的工程项目名（JNAME）  

```sql
select jname from j where city = '天津';
    jname    
-------------
 弹簧厂     
 造船厂     
(2 rows)
```

  9）查询在“精益”供应商下的零件，且质量小于15的零件详细信息

```sql
select distinct * from spj, s, p where spj.pno = p.pno 
and s.sno = spj.sno
and s.sname = '精益'
and p.weight<15;
 sno | pno | jno | qty | sno |  sname   | status |  city  | pno |  pname   | color | weight 
-----+-----+-----+-----+-----+----------+--------+--------+-----+----------+-------+--------
 S1  | P1  | J1  | 200 | S1  | 精益     | 20     | 天津   | P1  | 螺母     | 红    |     12
 S1  | P1  | J3  | 100 | S1  | 精益     | 20     | 天津   | P1  | 螺母     | 红    |     12
 S1  | P1  | J4  | 700 | S1  | 精益     | 20     | 天津   | P1  | 螺母     | 红    |     12
(3 rows)
```




## 实验三  
练习带连接的子查询操作  

6、复杂子查询操作

  1）在零件表中找出weight排名前三的零件名字(PNAME)，按降序输出  

```sql
select p.pname from p order by weight desc limit 3 offset 0;
  pname   
----------
 凸轮    
 齿轮    
 螺栓    
(3 rows)
```

  2）查询至少使用了供应商S1所供应的全部零件的城是(CITY)  



```sql
 select j.city 
 from j, spj A  
 where j.jno = A.jno 
 and not exists(
     select * 
     from spj B  
     where B.sno = 'S1' 
     and not exists (
         select * from spj 
         where A.pno = B.pno)
 );
 
 city 
------
(0 rows)
```

?? not solved:

天津是对应2个工程的，if这两个工程分别用了p1和p2，用这种方法是没法输出天津的

let's test: 

```sql
update spj set pno='P2' where jno='J4' and sno='S1';
UPDATE 1
spj=# select * from spj;
 sno | pno | jno | qty 
-----+-----+-----+-----
 S1  | P1  | J1  | 200
 S1  | P1  | J3  | 100
 S1  | P2  | J2  | 100
 S2  | P3  | J1  | 400
 S2  | P3  | J2  | 200
 S2  | P3  | J4  | 500
 S2  | P3  | J5  | 400
 S2  | P5  | J1  | 400
 S2  | P5  | J2  | 100
 S3  | P1  | J1  | 200
 S3  | P3  | J1  | 200
 S4  | P5  | J1  | 100
 S4  | P6  | J3  | 300
 S4  | P6  | J4  | 200
 S5  | P2  | J4  | 100
 S5  | P3  | J1  | 200
 S5  | P6  | J2  | 200
 S5  | P6  | J4  | 500
 S1  | P2  | J4  | 700
(19 rows)
select * from j;
 jno |    jname     |  city  
-----+--------------+--------
 J1  | 三建         | 北京  
 J2  | 一汽         | 长春  
 J3  | 弹簧厂       | 天津  
 J4  | 造船厂       | 天津  
 J5  | 机车厂       | 唐山  
 J6  | 无线电厂     | 常州  
 J7  | 半导体厂     | 南京  
(7 rows)
-- right answer: 天津(J3, J4) should be printed;
```

```sql
--right
create view spj_sub as (select pno, jno from spj where sno='S1');
CREATE VIEW
spj=# select * from spj_sub;
 pno | jno 
-----+-----
 P1  | J1
 P1  | J3
 P2  | J2
 P2  | J4
(4 rows)
 
select jc from j jc 
where jc.city in (select distinct city from j) 
and (select count(*) from (
     	select spj_sub.pno from j j1, spj_sub 
    		where j1.jno in (select j2.jno from j j2 where j2.city = jc.city) 
            and spj_sub.jno=j1.jno
		)
    z) 
 =
 (select count(*) from (select distinct pno from spj_sub) z2);
 
 --change to:(add a distinct before spj.pno)
select jc from j jc 
where jc.city in (select distinct city from j) 
and (select count(*) from (
     select distinct spj_sub.pno from j j1, spj_sub where j1.jno in (
         select j2.jno from j j2 where j2.city = jc.city) 
      and spj_sub.jno=j1.jno)
    z) 
 =
 (select count(*) from (select distinct pno from spj_sub) z2);
             jc              
-----------------------------
 (J3,"弹簧厂     ","天津  ")
 (J4,"造船厂     ","天津  ")
(2 rows)

--just change the jno into a set: (select j3.jno from j j3 where j3.city=j1.city)

--wrong1:
 select j.city 
 from j, spj A  
 where j.jno = A.jno 
 and not exists(
     select * 
     from spj B  
     where B.sno = 'S1' 
     and not exists (
         select * from spj 
         where A.pno = B.pno)
 );
 city 
------
(0 rows)
--wrong2:
select distinct j1 from j j1, spj A where not exists(
	select B.pno from spj B where B.sno='S1' and not exists(
		select * from spj C, j j2 where j2.jno in (
    		select j3.jno from j j3 where j3.city = j1.city) 
 				and C.jno = j2.jno and B.pno=C.pno));
 				
```

  

3）查询出供应商代码（SNO）为S1的，生产零件的全部颜色（COLOR）  

```sql
select p.color from p,spj where spj.sno = 'S1' and spj.pno = p.pno; 
 color 
-------
 红 
 红 
 红 
 绿 
(4 rows)
```

  4）查询所有WEIGHT > 20的零件名字(PNAME),零件代码(PNO),供应商代码(SNO)，供应商姓名(SNAME)  

```sql
select distinct spj.pno, spj.sno, s.sname from spj, s, p where p.weight > 20 and spj.pno = p.pno and spj.sno = s.sno; 
 pno | sno |   sname   
-----+-----+-----------
 P5  | S4  | 丰泰盛   
 P6  | S5  | 为民    
 P5  | S2  | 盛锡    
 P6  | S4  | 丰泰盛   
(4 rows)
```

  5）查询供应工程J1零件为红色的供应商号码(SNO)  

```sql
select distinct sno from spj, p where p.color = '红' and spj.pno = p.pno and spj.jno = 'J1';
 sno 
-----
 S1
 S3
(2 rows)
```

**Wrong:** if join s, will be:

```sql
select distinct s.sno from s, spj, p where p.color = '红' and spj.pno = p.pno and spj.jno = 'J1';
 sno 
-----
 S1
 S2
 S3
 S4
 S5
(5 rows)
-- change to :
select distinct s.sno from s, spj, p where p.color = '红' and spj.pno = p.pno and spj.jno = 'J1' and s.sno = spj.sno;
 sno 
-----
 S1
 S3
(2 rows)
```

mistake: need to `s.sno =spj.sno`

## 实验四
练习带分组聚集的查询

7、带分组聚集的查询操作

  1）查询大于平均WEIGHT的零件，列出他们的供应商代码（SNO），零件代码（PNO），工程代码（JNO），供应数量（QTY）  

Way1: 

```sql
select pno, sno, jno, qty from spj where pno in (select pno from p where weight > (select avg(weight) from p));

 pno | sno | jno 
-----+-----+-----
 P5  | S2  | J1
 P5  | S2  | J2
 P5  | S4  | J1
 P6  | S4  | J3
 P6  | S4  | J4
 P6  | S5  | J2
 P6  | S5  | J4
select spj.pno, spj.sno, spj.jno,spj.qty from spj, p where p.weight > (select avg(weight) from spj, p where spj.pno = p.pno) and spj.pno = p.pno;
 pno | sno | jno | qty 
-----+-----+-----+-----
 P5  | S2  | J1  | 400
 P5  | S2  | J2  | 100
 P5  | S4  | J1  | 100
 P6  | S4  | J3  | 300
 P6  | S4  | J4  | 200
 P6  | S5  | J2  | 200
 P6  | S5  | J4  | 500
(7 rows)
```

Way 2:

```sql
select pno into a from p where p.weight > (select avg(weight) from p);
select spj.pno, sno, jno, qty from spj, a where a.pno = spj.pno;
```

  

2）查询小于平均供应数量QTY的零件，列出他们的零件代码（PNO），零件名（PNAME），颜色（COLOR）  

```sql
select p.pno, pname, color,qty from p, spj where p.pno = spj.pno and spj.qty < (select avg(qty) from spj);
 pno |   pname   | color | qty 
-----+-----------+-------+-----
 P1  | 螺母      | 红    | 200
 P1  | 螺母      | 红    | 100
 P2  | 螺栓      | 绿    | 100
 P3  | 螺丝刀    | 蓝    | 200
 P5  | 凸轮      | 蓝    | 100
 P1  | 螺母      | 红    | 200
 P3  | 螺丝刀    | 蓝    | 200
 P5  | 凸轮      | 蓝    | 100
 P6  | 齿轮      | 红    | 200
 P2  | 螺栓      | 绿    | 100
 P3  | 螺丝刀    | 蓝    | 200
 P6  | 齿轮      | 红    | 200
(12 rows)
```

3）查询供应数量QTY不在99-301之间的零件，列出他们的零件代码（PNO），零件名（PNAME），颜色（COLOR）  

```sql
select p.pno, pname, color from spj, p where p.pno = spj.pno and spj.qty not between 99 and 301 group by p.pno;
 pno |   pname   | color 
-----+-----------+-------
 P5  | 凸轮      | 蓝 
 P6  | 齿轮      | 红 
 P3  | 螺丝刀    | 蓝 
 P1  | 螺母      | 红 
(4 rows)
```

  4）查询WEIGHT大于15，且供应数量QTY必须在250以上的零件，列出他们的零件代码（PNO），零件名（PNAME）,供应数量（QTY）  

```sql
 select p.pno, p.pname, p.color from p, spj where spj.pno = p.pno and p.weight > 15 and spj.qty >250 group by p.pno;
 pno |  pname   | color 
-----+----------+-------
 P6  | 齿轮     | 红 
 P5  | 凸轮     | 蓝 
(2 rows)
```



  5）查询工程项目代码（JNO）为“J1”的项目，列出所有使用的零件代码（PNO），零件名（PNAME）,颜色（COLOR）  

```sql
select p.pno, p.pname, spj.qty from p, spj where spj.jno = 'J1' and p.pno = spj.pno group by p.pno, spj.qty;
 pno |   pname   | qty 
-----+-----------+-----
 P1  | 螺母      | 200
 P3  | 螺丝刀    | 200
 P3  | 螺丝刀    | 400
 P5  | 凸轮      | 100
 P5  | 凸轮      | 400
(5 rows)

select p.pno, p.pname, spj.qty,sno from p, spj where spj.jno = 'J1' and p.pno = spj.pno group by p.pno, spj.qty, sno;
 pno |   pname   | qty | sno 
-----+-----------+-----+-----
 P1  | 螺母      | 200 | S1
 P1  | 螺母      | 200 | S3
 P3  | 螺丝刀    | 200 | S3
 P3  | 螺丝刀    | 200 | S5
 P3  | 螺丝刀    | 400 | S2
 P5  | 凸轮      | 100 | S4
 P5  | 凸轮      | 400 | S2
```

?? when groupby

  6）查询供应商代码（SNO），零件代码（PNO），重量（WEIGHT），通过零件代码（PNO），重量（WEIGHT）排序

```sql
select distinct spj.sno, spj.pno, p.weight from spj, p where spj.pno = p.pno order by  spj.pno, p.weight;
 sno | pno | weight 
-----+-----+--------
 S1  | P1  |     12
 S3  | P1  |     12
 S1  | P2  |     17
 S5  | P2  |     17
 S2  | P3  |     14
 S3  | P3  |     14
 S5  | P3  |     14
 S2  | P5  |     40
 S4  | P5  |     40
 S4  | P6  |     30
 S5  | P6  |     30
(11 rows)
```

## Tips:

>\password           设置密码。  
 q                  退出。  
 h                  查看SQL命令的解释，比如\h select    
 l                  列出所有数据库。  
 c [database_name]  连接其他数据库。  
 d                  列出当前数据库的所有表格。  
 d [table_name]     列出某一张表格的结构。  
 du                 列出所有用户。  
 e                  打开文本编辑器。  
 conninfo           列出当前数据库和连接的信息。  
 \?                  查看psql命令列表

## Note:

### 相关子查询

1. lab2.3）在零件表中查询平均重量在15以上的零件名字和零件代码（PNO）

   - 理解一：group by (pname, pno) 后计算平均重量，输出pname, pno

     ```sql
     spj=# select pname, pno from p group by (pname, pno) having avg(p.weight)>15;
       pname   | pno 
     ----------+-----
      凸轮     | P5
      螺栓     | P2
      齿轮     | P6
     (3 rows)
     ```

     错误：pno是唯一的，按照pno聚集等同于没聚集；如果更改为group by name，则无法select pno

   - 理解二：如果p1 螺丝刀weight为14， p2 螺丝刀weight为17， 则这两个螺丝刀的平均重量满足条件，最后需要输出这两对应的pname，pno【无法用group by实现，必须使用相关子查询】

