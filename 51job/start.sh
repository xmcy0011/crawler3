#!/bin/sh
start(){
  if [ -f "log.log" ];then
    # 所有log备份到这里
    if [ -d "log" ];then
      mkdir log
    fi

    mv log.log log.log.`date '+%Y%m%d %T'`
  fi

  nohup python3 jobMysql.py 2>&1 > log.log &
}

start
