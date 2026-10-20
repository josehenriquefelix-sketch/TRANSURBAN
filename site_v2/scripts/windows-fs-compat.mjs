import fs from 'node:fs';
// Some restricted Windows hosts reject the native realpath implementation even
// for ordinary files that the standard implementation can resolve. Keep all
// normal filesystem checks and fall back only for that native EPERM result.
if(process.platform==='win32'){
 const native=fs.realpathSync.native;
 fs.realpathSync.native=function(path,options){try{return native(path,options)}catch(error){if(error.code!=='EPERM')throw error;return fs.realpathSync(path,options)}};
}
