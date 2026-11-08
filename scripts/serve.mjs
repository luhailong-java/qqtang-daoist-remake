import {createAppServer} from '../server/app.mjs';

const app=createAppServer({port:Number(process.env.PORT||4387),host:'127.0.0.1'});
try{
  const address=await app.start();
  console.log(`QQ堂 · 道家Q版重制开发版\nLocal: http://127.0.0.1:${address.port}\n本机权威服务 / 人数遵循地图上限 / HTTP + SSE\n此服务不连接腾讯原运营服务器。`);
}catch(error){console.error(error.code==='EADDRINUSE'?'端口已被占用。请关闭旧预览，或设置PORT环境变量。':error.message);process.exitCode=1;}
for(const signal of ['SIGINT','SIGTERM'])process.once(signal,async()=>{await app.close();process.exit(0);});
