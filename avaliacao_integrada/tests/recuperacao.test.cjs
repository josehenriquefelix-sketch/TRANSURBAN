const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const c={window:{},URLSearchParams};vm.createContext(c);vm.runInContext(fs.readFileSync(path.join(__dirname,'../frontend/recuperacao.js'),'utf8'),c);const {read,entrada}=c.window.TransurbanRecovery;
function parse(url){const u=new URL(url,'http://127.0.0.1:8000');return read(u);}
test('link de recuperação padrão abre nova senha com token somente em memória',()=>{const r=parse('/#access_token=ficticio&type=recovery');assert.equal(r.active,true);assert.equal(r.token,'ficticio');});
test('link antigo com dois fragmentos não cai no dashboard',()=>{const r=parse('/#nova-senha#access_token=ficticio&type=recovery');assert.equal(r.active,true);assert.equal(r.token,'ficticio');});
test('rota dedicada preserva as três áreas',()=>{for(const area of ['passageiro','motorista','gestor']){const r=parse('/recuperar-senha?area='+area+'#access_token=ficticio&type=recovery');assert.equal(r.area,area);assert.equal(r.active,true);}});
test('endereço sem token ainda mostra recuperação e não abre o início',()=>{const r=parse('/recuperar-senha?area=gestor');assert.equal(r.active,true);assert.equal(r.token,'');});
test('link expirado remove token e exige outro link',()=>{const r=parse('/#error=access_denied&error_description=expirado&access_token=ficticio');assert.equal(r.failed,true);assert.equal(r.token,'');});
test('confirmação de cadastro não vira recuperação',()=>{assert.equal(parse('/#access_token=ficticio&type=signup').active,false);});
test('área externa não cria retorno aberto',()=>{assert.equal(parse('/recuperar-senha?area=https://example.invalid').area,'passageiro');assert.equal(entrada('https://example.invalid'),'/#login');assert.equal(entrada('gestor'),'/gestao/');});
