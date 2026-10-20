const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const output=process.env.EVIDENCIAS_SITE||path.resolve('evidencias/site-navegador-local');fs.mkdirSync(output,{recursive:true});
(async()=>{
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
const errors=[];const external=[];const dialogMessages=[];
async function context(gps){const c=await browser.newContext({viewport:{width:1440,height:1000},...(gps?{geolocation:{latitude:-23.425,longitude:-51.925,accuracy:15},permissions:['geolocation']}:{}),serviceWorkers:'block'});await c.route('**/*',r=>{const u=new URL(r.request().url());if(u.hostname==='127.0.0.1')return r.continue();external.push(u.origin);return r.abort();});return c;}
const dc=await context(true),pc=await context(false);const driver=await dc.newPage(),passenger=await pc.newPage();
for(const p of [driver,passenger]){p.on('pageerror',e=>errors.push(e.message));p.on('dialog',async d=>{dialogMessages.push(d.message());if(d.type()==='confirm')await d.accept();else await d.dismiss();});}
const url=(process.env.TRANSURBAN_TEST_URL||'http://127.0.0.1:8000')+'/app/';const stamp=Date.now();
async function register(page,name,role){await page.goto(url,{waitUntil:'domcontentloaded'});await page.getByRole('button',{name:'Criar conta',exact:true}).click();if(role==='motorista')await page.getByRole('button',{name:'Motorista',exact:true}).click();await page.locator('input[name=nome]').fill(name);await page.locator('input[name=email]').fill(`${role}.${stamp}@exemplo.com`);await page.locator('input[name=senha]').fill('SenhaTeste123!');await page.getByRole('button',{name:'Criar minha conta',exact:true}).click();await page.locator('.sidebar').waitFor();}
await driver.goto(url,{waitUntil:'domcontentloaded'});await driver.locator('#auth-form').waitFor();await driver.screenshot({path:path.join(output,'site-login-desktop.png')});
await register(driver,'Motorista QA','motorista');
await driver.locator('.sidebar [data-tab=planejar]').click();await driver.locator('#map').waitFor();
await driver.locator('#map').click({position:{x:160,y:130}});await driver.locator('.plan-point').first().waitFor();
await driver.locator('#map').click({position:{x:340,y:250}});await driver.locator('.plan-point').nth(1).waitFor();
await driver.locator('[data-point-name="0"]').fill('Embarque de teste');await driver.locator('[data-point-name="1"]').fill('Destino de teste');
await driver.getByRole('button',{name:'Salvar somente pontos, sem traçar rota',exact:true}).click();await driver.getByRole('button',{name:'Voltar para iniciar a viagem'}).waitFor();
await driver.getByRole('button',{name:'Voltar para iniciar a viagem'}).click();await driver.locator('input[name=veiculo]').fill('QA-01');await driver.locator('input[name=sentido]').fill('Ida de teste');
await driver.getByRole('button',{name:'Iniciar viagem de demonstração'}).click();await driver.locator('#gps-consent').waitFor();await driver.locator('#gps-consent').check();
await driver.getByRole('button',{name:'Compartilhar meu GPS',exact:true}).click();
await driver.waitForFunction(()=>document.body.innerText.includes('GPS recente'),{timeout:15000});
await register(passenger,'Passageiro QA','passageiro');await passenger.getByRole('button',{name:'Registrar embarque',exact:true}).waitFor();
await passenger.screenshot({path:path.join(output,'site-passageiro-desktop.png'),fullPage:false});
await passenger.getByRole('button',{name:'Registrar embarque',exact:true}).click();await passenger.getByRole('button',{name:'Confirmar meu embarque'}).click();
await passenger.getByRole('button',{name:'Registrar desembarque'}).waitFor();await passenger.locator('[data-action=report-occupancy][data-value=superlotado]').click();
await passenger.getByRole('button',{name:'Registrar desembarque'}).click();await passenger.getByRole('button',{name:'5 estrelas',exact:true}).click();
await passenger.locator('[data-action=review-occupancy][data-value=superlotado]').click();await passenger.locator('textarea[name=descricao]').fill('Avaliação QA: <img src=x onerror=alert(1)> deve aparecer como texto.');
await passenger.getByRole('button',{name:'Registrar avaliação',exact:true}).click();await passenger.getByText('Avaliação registrada: 5/5',{exact:true}).waitFor();
await driver.locator('.sidebar [data-tab=avaliacoes]').click();await driver.getByText('Avaliação QA: <img src=x onerror=alert(1)> deve aparecer como texto.',{exact:true}).waitFor();
if(await driver.locator('.review img').count())throw Error('Descrição criou HTML inseguro');
await passenger.locator('.sidebar [data-tab=carteira]').click();await passenger.getByRole('button',{name:'Simular recarga',exact:true}).click();await passenger.locator('[data-action=payment-method][data-value=credito]').click();
await passenger.locator('input[name=valor]').fill('50.00');await passenger.locator('select[name=parcelas]').selectOption('12');await passenger.getByRole('button',{name:'Simular crédito na carteira'}).click();
await passenger.locator('.balance').filter({hasText:'50,00'}).waitFor();
await passenger.getByRole('button',{name:'Simular VT',exact:true}).click();await passenger.locator('input[name=empresa]').fill('Empresa de teste');await passenger.locator('input[name=valor]').fill('100.00');await passenger.getByRole('button',{name:'Simular lançamento de VT'}).click();
await passenger.locator('.balance').filter({hasText:'150,00'}).waitFor();await passenger.reload({waitUntil:'domcontentloaded'});await passenger.locator('.sidebar [data-tab=carteira]').waitFor();await passenger.locator('.sidebar [data-tab=carteira]').click();await passenger.locator('.balance').filter({hasText:'150,00'}).waitFor();
await passenger.screenshot({path:path.join(output,'site-carteira-desktop.png'),fullPage:false});
await passenger.setViewportSize({width:390,height:844});await passenger.screenshot({path:path.join(output,'site-carteira-mobile.png'),fullPage:true});
const overflow=await passenger.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(overflow)throw Error('Página transborda no mobile');
await driver.locator('.sidebar [data-tab=viagem]').click();await driver.screenshot({path:path.join(output,'site-motorista-desktop.png'),fullPage:false});await driver.getByRole('button',{name:'Encerrar viagem',exact:true}).click();await driver.getByRole('heading',{name:'Nenhuma viagem iniciada'}).waitFor();
if(errors.length)throw Error(JSON.stringify(errors));if(dialogMessages.some(x=>x==='1'))throw Error('XSS executou alerta');
const report={ambiente:'Chromium Linux, dois contextos isolados. Não comprova GPS de dispositivo físico, mapa online, clima ou roteamento externo.',fluxos:['cadastro/login de motorista e passageiro','planejamento de dois pontos sem desenho de via fictícia','início de viagem e GPS emulado exclusivamente no teste','embarque, lotação superlotado e desembarque','avaliação 5 estrelas e descrição como texto, sem XSS','crédito de demonstração parcelado em 12 e VT de teste','persistência de sessão e saldo após recarregar','viewport 390px sem transbordamento horizontal','encerramento da viagem pelo motorista'],saldo_demo_centavos:15000,erros_javascript:errors,servicos_externos:'Bloqueados no navegador; mensagens de indisponibilidade exercitadas.',aprovado:true};fs.writeFileSync(path.join(output,'site-web-browser.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
