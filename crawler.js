// Load the http module to create an http server.                                                                                                                                                                      \
                                                                                                                                                                                                                        
var http = require('http');

fs = require("fs")
fs.readFile("stock-list.txt",'utf8',function(err,data){
    if (err) {
        return console.log(err);
    };
    var array = data.toString().split("\n");
    for (var i = 1; i < array.length; i++) {
        console.log(array[i])
    };
})


var prevStockInfo = {};

var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/sina_data');

var StockModel = mongoose.model('Stock',{"_id":String, "data":Array});


function arraysIdentical(a, b) {
    if (!a || ! b) return false;
    var i = a.length;
    if (i != b.length) return false;
    while (i--) {
        if (a[i] !== b[i]) return false;
    }
    return true;
};

function getStockInfo(i) {

    var stockName = 'sh'+stockCodes[i]

    var options = {
        host: 'hq.sinajs.cn',
        port: 80,
        path: '/list='+stockName
    };


    http.get(options, function(res) {
        res.on('data', function(chunk) {
            eval(chunk.toString());
            var stockNameVar = eval("hq_str_"+stockName);
            var stockInfoArray = stockNameVar.split(",");
            if (arraysIdentical(stockInfoArray,prevStockInfo[i])) {
                console.log("identical "+stockName);
            } else {
                console.log("writing to DB "+stockName);
                //write to DB                                                                                                                                                                                           
                var stock = new StockModel({"_id":stockName+"_"+stockInfoArray[stockInfoArray.length-3]+"_"+stockInfoArray[stockInfoArray.length-2],"data":stockInfoArray});
                stock.save(function (err) {
                    if (err) console.log(err);
                    console.log('inserted');
                });

                prevStockInfo[i] = stockInfoArray;
            }
    });
}).on("error", function(e) {
    console.log("got error" + e.message);
    });
}

var i = 0;
while (i < 0) {
    getStockInfo(i%15);
    i ++;
}