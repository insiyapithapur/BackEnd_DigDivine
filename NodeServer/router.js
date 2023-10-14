const express = require("express");
const router = express.Router();
require('dotenv').config()
const axios = require('axios');
const crypto = require('crypto');
const algorithm = 'aes-256-cbc'; //Using AES encryption
const key = crypto.randomBytes(32);
const iv = crypto.randomBytes(16);




const host_url = process.env.TEAMSBUILDERS_URL

const ActivationApi = async (user_id, app_name, order_num) => {
    setTimeout(()=>{
        let data= "";
        var config = {
            method: 'get',
            url: host_url+`/v1/api/check/${user_id}/activation?appname=${app_name}&order_num=${order_num}&money_generate=True`,
            headers: { 
              'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI'
            },
            data : data
          };
          
        axios(config)
        .then(function (response) {
        console.log(JSON.stringify(response.data.status));
        })
        .catch(function (error) {
        console.log("err",error.response.data);
        }); 
    },5000)
}

const getUrl = (app_name) => {
    switch(app_name) {
      case "vestige":
        return "/vestige";
      case "hhi":
        return "/hhi";
      case "proteinWorld":
        return "/protein-world";
      case "amulyaHerbal":
        return "/amulya-herbs";
      default:
        return "";
    }
  }

const AddUserBv = async (user_id, order_num, app_name, auth_heder) => {
    console.log("userId", user_id, order_num, app_name);
    setTimeout(() =>{
        var data = JSON.stringify({
            "order_num": parseInt(order_num),
          });
          
          var config = {
            method: 'post',
            url: host_url+`${getUrl(app_name)}/api/userbv/${user_id}/`,
            headers: { 
              'Content-Type': 'application/json', 
              'Cookie': 'csrftoken=EUQ1DoHGzmryjVtkrFagOe7X9VbmYDz37CLuvW2AQHq6VWgfL8fj9LzjnZVo0yZI',
            },
            data : data
          };
          if(auth_heder){
            config.headers['Authorization'] = auth_heder
          }
          
          axios(config)
          .then(function (response) {
            console.log(JSON.stringify(response.data));
          })
          .catch(function (error) {
            console.log(error.response.data);
          });
    }, 5000)
}

async function CallActivation(){
    setTimeout(()=>{
        ActivationApi()
    },5000)
}

router.post("/activate", (req, res) => {
    if(!req.query.user_id || !req.query.app_name || !req.query.order_num){
        return res.status(400).send({
            message: "Activate content can not be empty"
        });
    }
    ActivationApi(req.query.user_id, req.query.app_name, req.query.order_num)
    res.status(200).send({status:"ok",message:"Create a new workout"});
  });

router.post('/bvaddition', (req, res) => {
    if(!req.query.user_id || !req.query.order_num){
        return res.status(400).send({
            message: "Order number can not be empty"
        });
    }

    AddUserBv(req.query.user_id, req.query.order_num, req.query.app_name, req.headers.authorization);
    res.status(200).send({status:"ok",message:"Create a new workout"});
})


function encrypt(text) {
    let cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key), iv);
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    return { iv: iv.toString('hex'), encryptedData: encrypted.toString('hex') };
}
 
 // Decrypting text
function decrypt(text) {
    let iv = Buffer.from(text.iv, 'hex');
    let encryptedText = Buffer.from(text.encryptedData, 'hex');
    let decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key), iv);
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    return decrypted.toString();
}

router.post("/encrypt", (req, res) =>{
    let input_data = req.body.input_data
    if(typeof input_data === 'object'){
        input_data = JSON.stringify(input_data);
    }
    return res.status(200).send({status:"ok","result":encrypt(input_data)})
})


router.post("/decrypt", (req, res) =>{
    let encrypted_data = req.body.encrypted_data
    
})

module.exports = router;