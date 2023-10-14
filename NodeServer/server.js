var express = require('express');
var app = express();
require('dotenv').config()
const appRouter = require('./router');
const cron = require('node-cron');
const axios = require('axios');
const bodyParser = require('body-parser');
const http = require('http');
const httpServer = http.Server(app);

const cors = require('cors');

app.use(cors());
app.options('*', cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

const io = require('socket.io')(httpServer, { 
  cors: "*"
});


app.use("/api", appRouter)

const host_url = process.env.TEAMSBUILDERS_URL


cron.schedule('0 0 * * *', function() {
    BillReset();
});
  
cron.schedule('55 23 * * *', function() {
  MoneyGenerationReset();
});

const BillReset = () => {
    var config = {
        method: 'post',
        url: host_url + '/v1/api/clear/activation-bill',
        headers: { 
          'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI'
        }
      };
      
      axios(config)
      .then(function (response) {
        console.log(JSON.stringify(response.data));
      })
      .catch(function (error) {
        console.log("err",error.response.data);
      });
}

const MoneyGenerationReset = () => {
  var config = {
    method: 'post',
    url: host_ur = '/v1/api/clear/money-generate?appname=allapps',
    headers: { 
      'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI'
    }
  };
  
  axios(config)
  .then(function (response) {
    console.log(JSON.stringify(response.data));
  })
  .catch(function (error) {
    console.log(error);
  });
  
}

// WEBSOCKETS
let Clients = [];
io.use((socket, next) => {
  var authParams = socket.handshake.query;
  if(authParams == undefined){
      console.log("Client couldn't connect");
  }
  
  var clientInfo = new Object();
  clientInfo.user_id = authParams.id;
  clientInfo.clientId = socket.id;
  if(!Clients.some(client => client.user_id === data.user_id)){
    Clients.push(clientInfo);
  }
  next()
})


io.on('connect', socket => {
    console.log('a user connected!', socket.id)

    socket.on('disconnect', () => {
      console.log('user disconnected!', socket.id);
      Clients = Clients.filter(client => client.clientId !== socket.id)
    })
  })

// SSE

app.get('/checkout', (req, res) => {
  let user_id = req.query.user_id;
  let client = Clients.find(ClientInfo => ClientInfo.user_id == user_id);
  io.to(client.clientId).emit('test', {"text":"hii there"})
  res.send("hiii")
})


app.get('/check', (req, res) => {
  console.log("clients", Clients)
  res.send("hiii")
})


httpServer.listen(8081, () => {
  console.log("Server is running on the port 8081");
})