(()=>{function e(e,t,o){try{window.parent!==window.self&&window.parent.postMessage({event:e,data:t},`https://www.opentable.${o}`)}catch(e){}}const t=document.location.hostname.split("opentable.")[1]||"com",o=new URLSearchParams(document.location.search).get("fbclid"),n=document.cookie.split("; ");let c=n.find((e=>e.startsWith("_fbp=")))?.split("=")[1],a=n.find((e=>e.startsWith("_fbc=")))?.split("=")[1];if(!c||!a&&o){const n=Date.now(),i=Math.floor(Math.random()*(Number.MAX_SAFE_INTEGER-1)+1),s=c?void 0:`fb.1.${n}.${i}`,r=o&&!a?`fb.1.${n}.${o}`:void 0,d=new Date;d.setMonth(d.getMonth()+1);const m=`; SameSite=none; Secure; path=/; domain=.opentable.${t}; expires=${d.toUTCString()}`;s&&(c=s,document.cookie=`_fbp=${s}${m}`),r&&(a=r,document.cookie=`_fbc=${r}${m}`),e("meta-cookies-created",{fbp:s,fbc:r},t)}const i=new URLSearchParams;i.set("id","725308910857169"),i.set("ev","PageView"),i.set("fbp",c),a&&i.set("fbc",a);const s=`https://www.facebook.com/tr?${i.toString()}`,r=document.createElement("img");r.referrerPolicy="origin",r.src=s,document.body.appendChild(r),e("meta-pixel-created",{metaPageViewPixelUrl:s},t);try{const e=document.createElement("img");e.src=`https://www.opentable.com/dapi/v1/track/pixel/meta?${i.toString()}`,document.body.appendChild(e)}catch(e){}})();