# -*- coding:utf-8 -*-
#
# File      : pkgsdb.py
# This file is part of RT-Thread RTOS
# COPYRIGHT (C) 2006 - 2018, RT-Thread Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Change Logs:
# Date           Author          Notes
# 2018-5-28      SummerGift      Add copyright information
# 2020-4-10      SummerGift      Code clear up
#

import sqlite3
import os
import hashlib
from ..pkgs.cmd_package_utils import user_input
from .vars import Import
from .settings import config

SHOW_SQL = False


def get_file_md5(filename):
    if not os.path.isfile(filename):
        return
    hash_value = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        hash_value.update(b)
    f.close()
    return hash_value.hexdigest()


def get_conn(path):
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        return conn
    else:
        print('on memory:[:memory:]')
        return sqlite3.connect(':memory:')


def close_all(conn):
    if conn is not None:
        conn.close()


def get_cursor(conn):
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()


def create_table(conn, sql):
    if sql is not None and sql != '':
        cu = get_cursor(conn)
        if SHOW_SQL:
            print('execute :[{}]'.format(sql))
        cu.execute(sql)
        conn.commit()
        close_all(conn)
    else:
        print('the [{}] is empty or equal None!'.format(sql))


def save(conn, sql, data):
    """insert data to database"""
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            for d in data:
                if SHOW_SQL:
                    print('execute sql:[{}],arguments:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn)
    else:
        print('the [{}] is empty or equal None!'.format(sql))


def isdataexist(pathname):
    ret = True
    dbfilename = Import('dbsqlite_pathname')

    conn = get_conn(dbfilename)
    c = get_cursor(conn)
    sql = 'SELECT md5 from packagefile where pathname = "' + pathname + '"'
    cursor = c.execute(sql)
    for row in cursor:
        dbmd5 = row[0]

    if dbmd5:
        ret = False
    conn.close()
    return ret


# Add data to the database, if the data already exists, don't add again
def save_to_database(pathname, package_pathname, before_change_name):
    db_pathname = Import('dbsqlite_pathname')
    # bsp_root = Import('bsp_root')
    bsp_root = config.BSP_DIR
    bsp_packages_path = os.path.join(bsp_root, 'packages')

    conn = get_conn(db_pathname)
    save_sql = '''insert into packagefile values (?, ?, ?)'''
    package = os.path.basename(package_pathname)
    md5pathname = os.path.join(bsp_packages_path, before_change_name)

    if not os.path.isfile(md5pathname):
        print("md5pathname is Invalid")

    md5 = get_file_md5(md5pathname)
    data = [(pathname, package, md5)]
    save(conn, save_sql, data)


def dbdump(dbfilename):
    conn = get_conn(dbfilename)
    c = get_cursor(conn)
    cursor = c.execute("SELECT pathname, package, md5 from packagefile")
    for row in cursor:
        print("pathname = ", row[0])
        print("package = ", row[1])
        print("md5 = ", row[2], "\n")
    conn.close()


def remove_unchanged_file(pathname, dbfilename, dbsqlname):
    """delete unchanged files"""
    flag = True

    conn = get_conn(dbfilename)
    c = get_cursor(conn)
    filemd5 = get_file_md5(pathname)
    dbmd5 = 0

    sql = 'SELECT md5 from packagefile where pathname = "' + dbsqlname + '"'
    # print sql
    cursor = c.execute(sql)
    for row in cursor:
        # fetch md5 from database
        dbmd5 = row[0]

    if dbmd5 == filemd5:
        # delete file info from database
        sql = "DELETE from packagefile where pathname = '" + dbsqlname + "'"
        conn.commit()
        os.remove(pathname)
    else:
        print("%s has been changed." % pathname)
        print('Are you sure you want to permanently delete the file: %s?' %
              os.path.basename(pathname))
        print('If you choose to keep the changed file,you should copy the file to another folder. '
              '\nbecaues it may be covered by the next update.')

        rc = user_input('Press the Y Key to delete the folder or just press Enter to keep it : ')
        if rc == 'y' or rc == 'Y':
            sql = "DELETE from packagefile where pathname = '" + dbsqlname + "'"
            conn.commit()
            os.remove(pathname)
            print("%s has been removed.\n" % pathname)
        else:
            flag = False
    conn.close()
    return flag


# 删除一个包，如果有文件被改动，则提示(y/n)是否要删除，输入y则删除文件，输入其他字符则保留文件。
# 如果没有文件被改动，直接删除文件夹,包文件夹被完全删除返回true，有被修改的文件没有被删除返回false
def deletepackdir(dirpath, dbpathname):
    flag = getdirdisplay(dirpath, dbpathname)

    if flag:
        if os.path.exists(dirpath):
            for root, dirs, files in os.walk(dirpath, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(dirpath)
        # print "the dir should be delete"
    return flag


# walk through all files in filepath, include subfolder
def displaydir(filepath, basepath, length, dbpathname):
    flag = True
    if os.path.isdir(filepath):
        files = os.listdir(filepath)
        for fi in files:
            fi_d = os.path.join(filepath, fi)
            if os.path.isdir(fi_d):
                displaydir(fi_d, basepath, length, dbpathname)
            else:
                pathname = os.path.join(filepath, fi_d)
                dbsqlname = basepath + os.path.join(filepath, fi_d)[length:]
                if not remove_unchanged_file(pathname, dbpathname, dbsqlname):
                    flag = False
    return flag


def getdirdisplay(filepath, dbpathname):
    display = filepath
    length = len(display)
    basepath = os.path.basename(filepath)
    flag = displaydir(filepath, basepath, length, dbpathname)
    return flag
