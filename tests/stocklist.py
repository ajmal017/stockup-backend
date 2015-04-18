import motor
import tornado
from tornado import options
from tornado.ioloop import IOLoop
import logging
#import config
from tornado import gen

fp = open("../stock-list.txt","w+")
@gen.coroutine
def getstocknumber():
    client = motor.MotorClient('119.29.16.193')
    db=client.ss_test
    cursor = yield db.stock_catalog.find_one()

    code_name_dict = cursor["code_name_dict"]

    try:
        for iter in code_name_dict.keys():
	    print(iter)
            fp.write(iter)
            fp.write("\r\n")
        fp.close()
    except Exception as e:
        print(e)
        return

    print('done')
def main():
    getstocknumber()


if __name__== "__main__":
    tornado.options.parse_command_line()
    main()
    IOLoop.instance().start()


