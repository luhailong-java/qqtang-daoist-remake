let token=sessionStorage.getItem('qqtang-rebuild-token')||'';
let source=null,onSnapshot=()=>{},onStatus=()=>{};
async function request(path,body){
  const response=await fetch(path,{method:body===undefined?'GET':'POST',headers:{...(body===undefined?{}:{'Content-Type':'application/json'}),...(token?{Authorization:'Bearer '+token}:{})},...(body===undefined?{}:{body:JSON.stringify(body)})});
  let data;try{data=await response.json();}catch{throw new Error('本地服务返回格式不正确。');}
  if(!response.ok){if(response.status===401){token='';sessionStorage.removeItem('qqtang-rebuild-token');source?.close();onStatus(false);}throw new Error(data.error||'请求未完成');}return data;
}
function connect(){
  source?.close();source=new EventSource('/api/events?token='+encodeURIComponent(token));
  source.addEventListener('data',event=>{try{onSnapshot(JSON.parse(event.data));onStatus(true);}catch(error){console.error('快照显示失败',error);}});
  source.onopen=()=>onStatus(true);source.onerror=()=>onStatus(false);
}
export const network={
  get hasSession(){return !!token;},
  async maps(){return request('/api/maps');},
  async map(id){return request('/api/maps/'+encodeURIComponent(id));},
  async restore(snapshot,status){onSnapshot=snapshot;onStatus=status;if(!token)return false;try{onSnapshot(await request('/api/state?token='+encodeURIComponent(token)));connect();return true;}catch{return false;}},
  async login(name,character,snapshot,status){onSnapshot=snapshot;onStatus=status;const data=await request('/api/session',{name,character});token=data.token;sessionStorage.setItem('qqtang-rebuild-token',token);const state=await request('/api/state?token='+encodeURIComponent(token));onSnapshot(state);connect();return state;},
  async create(config){const data=await request('/api/rooms',config);onSnapshot(data);return data;},
  async join(id){const data=await request('/api/rooms/'+encodeURIComponent(id)+'/join',{});onSnapshot(data);return data;},
  async action(action,fields={}){const data=await request('/api/action',{action,...fields});onSnapshot(data);return data;},
  async input(input){return request('/api/input',input);},
  async logout(){try{await this.action('leave');}catch{}source?.close();token='';sessionStorage.removeItem('qqtang-rebuild-token');},
};
