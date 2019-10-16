1. start: `sudo -u postgres psql`

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