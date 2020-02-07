# hunt_game_mysql文件说明

1. HuntGame是一个package
   - \__init__.py: 
     - 配置app
     - 定义db
     - 定义bcrypt
     - 定义login_manager
   - routes.py:
     - JSON API
   - utils.py:
     - add_character(...)
     - count_competence(...)
     - and so on...
2. run.py: 
   - 运行app
   - 运行scheduler
   - 运行对scheduler的测试函数test_auto_jobs()
3. test.py:
   - 定义并运行测试函数
   - 需要在run.py已运行的前提下运行