import {env} from 'cloudflare:workers';
import {getChatGPTUser} from '../../chatgpt-auth';
import {handleApi} from '../../../lib/api.mjs';
export const dynamic='force-dynamic';
async function handler(request:Request){return handleApi(request,{db:env.DB,user:await getChatGPTUser()});}
export const GET=handler;
export const POST=handler;
