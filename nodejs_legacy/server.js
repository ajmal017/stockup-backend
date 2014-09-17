var express = require('express');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var session = require('express-session');
var app = express();
app.use(bodyParser());
app.use(cookieParser());
app.use(session({ secret: 'stocktest', cookie: { maxAge: 60000 }}));
app.use(function (req, res, next) {
    var sess = req.session;
    if (sess.views) {
        sess.views++;
        res.setHeader('Content-Type', 'text/html');
        res.write('<p>views: ' + sess.views + '</p>');
        res.write('<p>expires in: ' + (sess.cookie.maxAge / 1000) + 's</p>');
        next();
    } else {
        sess.views = 1
        res.send('welcome to the session demo 1. refresh!');
        next();
    }
});

app.get('/', function (req, res) {
    /*console.log(req.param('user'));
     console.log(req.param('pass'));
     console.log("happy");*/
    res.send('welcome get');
});

app.post('/login', function (req, res) {
    var post_body = req.body;
});

app.listen(8000);
console.log('server started on port' + 8000);