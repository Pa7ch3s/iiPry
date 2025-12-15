import{a9 as A,aa as R,ab as J,ac as M,ad as $,ae as C,af as O}from"./index-BnTlsbFl.js";import{w as F}from"./import-DfaWnrdO.js";import{b,f as B,t as P,g as D,h as L,i as V}from"./index-wZAP8gf2.js";const E=t=>t.replace(/'/g,"\\'"),d=(t,e)=>{if(!t||t<0)return e;const s=new Array(t+1).join("  ");return e.split(`
`).map(r=>s+r).join(`
`)},te=t=>{const e=["const { expect } = chai;","","// Clear active request before test starts (will be set inside test)","beforeEach(() => insomnia.clearActiveRequest());",""];for(const s of t||[])e.push(...T(0,s));return e.join(`
`)},T=(t,e)=>{if(!e)return[];const s=[];s.push(d(t,`describe('${E(e.name)}', () => {`));const r=e.suites||[];for(const[i,a]of r.entries())i!==0&&s.push(""),s.push(...T(t+1,a));const u=e.tests||[];for(const[i,a]of u.entries())(r.length>0||i!==0)&&s.push(""),s.push(...k(t+1,a));return s.push(d(t,"});")),s},k=(t,e)=>{if(!e)return[];const s=[];s.push(d(t,`it('${E(e.name)}', async () => {`));const{defaultRequestId:r}=e;return typeof r=="string"&&(s.push(d(t,"// Set active request on global insomnia object")),s.push(d(t,`insomnia.setActiveRequestId('${r}');`))),e.code&&s.push(d(t+1,e.code)),s.push(d(t,"});")),s},n=require("mocha");n.utils;n.interfaces;const U=n.reporters;n.Runnable;n.Context;n.Runner;n.Suite;n.Hook;n.Test;n.afterEach;n.after;n.beforeEach;n.before;n.describe;n.it;n.xdescribe;n.xit;n.setup;n.suiteSetup;n.suiteTeardown;n.suite;n.teardown;n.test;n.run;n.unloadFile;class G{activeRequestId;activeEnvironmentId=null;sendRequest;constructor(e){this.sendRequest=e.sendRequest,this.activeRequestId=null}setActiveRequestId(e){this.activeRequestId=e}clearActiveRequest(){this.activeRequestId=null}async send(e=null){const s=e||this.activeRequestId;if(!s)throw new Error("No selected request");return await this.sendRequest(s)}}class W extends U.Base{description="single JS object";constructor(e,s){super(e,s),n.reporters.Base.call(this,e,s);const r=this,u=[],i=[],a=[],p=[];e.on(n.Runner.constants.EVENT_TEST_END,o=>{u.push(o)}),e.on(n.Runner.constants.EVENT_TEST_PASS,o=>{p.push(o)}),e.on(n.Runner.constants.EVENT_TEST_FAIL,o=>{a.push(o)}),e.on(n.Runner.constants.EVENT_TEST_PENDING,o=>{i.push(o)}),e.once(n.Runner.constants.EVENT_RUN_END,()=>{e.testResults={stats:r.stats,tests:u.map(m),pending:i.map(m),failures:a.map(m),passes:p.map(m)}})}}const m=t=>{let e=t.err||{};return e instanceof Error&&(e=Q(e)),{id:t.id,title:t.title,fullTitle:t.fullTitle(),file:t.file,duration:t.duration,currentRetry:t.currentRetry(),err:H(e)}},H=t=>{const e=[];return JSON.parse(JSON.stringify(t,(s,r)=>{if(typeof r=="object"&&r!==null){if(e.includes(r))return""+r;e.push(r)}return r}))},Q=t=>Object.getOwnPropertyNames(t).reduce((e,s)=>({...e,[s]:t[s]}),{});function z(t){return`
  const externalModules = new Map([['chai', global.chai], ['chai-json-schema', global.chaiJSONSchema]]);

  const requireInterceptor = (moduleName) => {
    if (
      [
        // node.js modules
        'path',
        'assert',
        'buffer',
        'util',
        'url',
        'punycode',
        'querystring',
        'string_decoder',
        'stream',
        'timers',
        'events',
        // follows should be npm modules
        // but they are moved to here to avoid introducing additional dependencies
      ].includes(moduleName)
    ) {
      return require(moduleName);
    } else if (['atob', 'btoa'].includes(moduleName)) {
      return moduleName === 'atob' ? atob : btoa;
    } else if (externalModules.has(moduleName)) {
      const externalModule = externalModules.get(moduleName);
      if (!externalModule) {
        throw Error(\`no module is found for "\${moduleName}"\`);
      }
      return externalModule;
    }
  
    throw Error(\`no module is found for "\${moduleName}"\`);
  };

  require = requireInterceptor;
  
${t}`}const K=async(t,e,s="spec",r)=>new Promise((u,i)=>{const{bail:a,keepFile:p,testFilter:o}=e;global.insomnia=new G(e),b.use(require("chai-json-schema")),global.chai=b,global.chaiJSONSchema=require("chai-json-schema");const l=new n({timeout:1e3*60*1,globals:["insomnia","chai"],bail:a,reporter:s,fgrep:o});(Array.isArray(t)?t:[t]).forEach(c=>{l.addFile(X(z(c)))});try{const c=l.run(()=>{if(u(r(c)),delete global.insomnia,delete global.chai,delete global.chaiJSONSchema,p&&l.files.length){console.log(`Test files: ${JSON.stringify(l.files)}.`);return}l.files.forEach(h=>{A(h,f=>{f&&console.log("Failed to clean up test file",h,f)})})})}catch(c){i(c)}}),X=t=>{const e=R(F(),"insomnia-testing");J.mkdirSync(e,{recursive:!0});const s=R(e,`${crypto.randomUUID()}-test.ts`);return M(s,t),s},se=async(t,e)=>K(t,e,W,s=>s.testResults);function ne(){return async function(e){$.incrementExecutedRequests();const{request:s,environment:r,settings:u,clientCertificates:i,caCert:a,activeEnvironmentId:p,timelinePath:o,responseId:l}=await B(e),g=await P({request:s,environment:r._id,purpose:"send"}),c=await D(g);C(c);const h=await L(c,i,a,u,o,l),f=await V(h,p,c,g.context),{statusCode:y,statusMessage:N,headers:S,elapsedTime:w}=f,I=S?.reduce((x,{name:_,value:j})=>({...x,[_.toLowerCase()||""]:j||""}),[]),q=await O(f),v=q?q.toString("utf8"):void 0;return{status:y,statusMessage:N,data:v,headers:I,responseTime:w}}}export{ne as a,te as g,se as r};
//# sourceMappingURL=unit-test-feature-CNk-Sfkl.js.map
