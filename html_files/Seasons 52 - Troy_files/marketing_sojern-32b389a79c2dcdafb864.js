(()=>{const e=new URLSearchParams(document.location.search).get("partner_uid");if(e){const t=new URLSearchParams;t.set("partner_uid",e);const n=`https://pixel.sojern.com/pixel/partnersync/LiVxPJZQ9kZBmt7a?${t.toString()}`,r=document.createElement("img");r.referrerPolicy="origin",r.src=n,document.body.appendChild(r);try{const e=document.createElement("img");e.src=`https://www.opentable.com/dapi/v1/track/pixel/sojern?${t.toString()}`,document.body.appendChild(e)}catch(e){}}})();