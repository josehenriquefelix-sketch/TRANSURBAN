import Dashboard from './dashboard';
import {getChatGPTUser,chatGPTSignInPath,chatGPTSignOutPath} from './chatgpt-auth';
export const dynamic='force-dynamic';
export default async function Home(){const user=await getChatGPTUser();return <Dashboard identity={user?{name:user.displayName}:null} signIn={chatGPTSignInPath('/')} signOut={chatGPTSignOutPath('/')}/>;}
