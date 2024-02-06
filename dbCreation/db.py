
import sys, os, os.path, stat, sqlite3

def create_db(sql_filename, new_db = 1):
  if new_db:
    try: os.unlink(sql_filename)
    except: pass
  db = sqlite3.connect(sql_filename)
  return db

def do_sql(db_cursor, sql, arg = ()):
  #print(sql)
  db_cursor.execute(sql, arg)

def close_db(db, sql_filename = u"", close = 1, set_readonly = 1):
  if close:
    db.commit()
    db.close()
  if set_readonly:
    os.chmod(sql_filename, stat.S_IREAD | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

def read_file(filename, encoding = "utf8"):
  if sys.version[0] == "2":
    if encoding: return open(filename).read().decode(encoding)
    else:        return open(filename).read() # XXX ?
  else:
    if encoding: return open(filename, encoding = encoding).read()
    else:        return open(filename, mode = "rb").read()

def write_file(filename, content, encoding = "utf8"):
  if sys.version[0] == "2":
    if encoding: open(filename, "w").write(content.encode("utf8"))
    else:        open(filename, "w").write(content) # XXX ?
  else:
    if encoding: return open(filename, "w", encoding = encoding).write(content)
    else:        return open(filename, "wb").write(content)
