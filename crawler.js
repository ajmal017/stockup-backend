// Load the http module to create an http server.                                                                                                                                                                      \

var http = require('http');
var iconv = require('iconv-lite');


var prevStockInfo = {};

var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/ss/');

var StockSchema = new Schema({"_id":{"c":Number,"d":Date}, "d":Array}, {autoIndex:false})
var StockModel = mongoose.model('Stock', StockSchema, 'stocks');

fs = require("fs");
fs.readFile("stock-list.txt",'utf8',function(err,data){
    if (err) {
        console.log(err);
    };
    var stockNames = [];

    var array = data.toString().split("\n");
    for (var i = 1; i < array.length; i++) {
        if (array[i][0] == "#" || array[i].length < 3) {continue};
        var stockName = parseInt(array[i].split(" ")[1]);
        stockNames.push(stockName);
    };


    a = stockNames.slice(20,35)
    getStockInfo(a)
    setInterval(getStockInfo,3000,a)
})




function arraysIdentical(a, b) {
    if (!a || ! b) return false;
    var i = a.length;
    if (i != b.length) return false;
    while (i--) {
        if (a[i] !== b[i]) return false;
    }
    return true;
};

function getStockInfo(names) {
    var stockNameString = ""
    for (var i = names.length - 1; i >= 0; i--) {
        stockNameString += 'sh'+names[i] + ','
    };
    var options = {
        host: 'hq.sinajs.cn',
        port: 80,
        path: '/?list='+stockNameString
    };

    http.get(options, function(res) {
        res.on('data', function(chunk) {
            try {
                str = iconv.decode(chunk, 'GB18030');
                eval(str.toString());
                for (var i = names.length - 1; i >= 0; i--) {
                    var stockName = names[i]
                    var stockNameVar = eval("hq_str_sh"+stockName);
                    var stockInfoArray = stockNameVar.split(",");
                    var dateString = stockInfoArray[stockInfoArray.length-3]+"T"+stockInfoArray[stockInfoArray.length-2];
                    var dateObj = new Date(dateString);

                    if (arraysIdentical(stockInfoArray,prevStockInfo[i])) {
                        console.log("identical "+stockName);
                    } else {
                        console.log("writing to DB "+stockName);
                        //write to DB                                                                                                                                                                                           
                        var stock = new StockModel({"_id":{"c":stockName,"d":dateObj},"d":stockInfoArray});
                        stock.save(function (err) {
                            if (err) console.log(err);
                            else console.log('inserted');
                        });

                        prevStockInfo[i] = stockInfoArray;
                    }
                };
            } catch (err) {
                console.log(err);
            }
            
            
        });
    }).on("error", function(e) {
        console.log("got error" + e.message);
    });
}

