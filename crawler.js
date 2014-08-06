// Load the http module to create an http server.                                                                                                                                                                      \
                                                                                                                                                                                                                        
var http = require('http');

var stockNames = [];

fs = require("fs");
fs.readFile("stock-list.txt",'utf8',function(err,data){
    if (err) {
        return console.log(err);
    };
    var array = data.toString().split("\n");
    for (var i = 1; i < array.length; i++) {
        if (array[i][0] == "#" || array[i].length < 3) {continue};
        var stockName = parseInt(array[i].split(" ")[1]);
        stockNames.push(stockName);
    };
    console.log(stockNames);
})



var prevStockInfo = {};

var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/ss/real_data');

var StockModel = mongoose.model('Stock',{"_id":{"c":Number,"d":Date}, "d":Array});


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
    var stockName = 'sh'+stockCodes[i]
    for (var i = names.length - 1; i >= 0; i--) {
        names[i]
    };
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
            var dateString = stockInfoArray[stockInfoArray.length-3]+"T"+stockInfoArray[stockInfoArray.length-2];
            var dateObj = new Date(dateString);

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