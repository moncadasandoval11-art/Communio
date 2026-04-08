import { useState } from "react";

const GF = `@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');`;

const SAMPLE_DATA = [
  {
    id: 1, parish: "Cathedral of St. Ignatius Loyola", city: "Palm Beach Gardens",
    events: [
      { id: 101, name: "Sunday High Mass", date: "Sunday", time: "10:00 AM", category: "Mass", description: "Solemn High Mass with full choir. All are welcome to receive the Eucharist.", recurring: true },
      { id: 102, name: "Sacrament of Confession", date: "Saturday", time: "3:30 PM", category: "Confession", description: "Sacrament of Reconciliation offered before the Saturday vigil Mass.", recurring: true },
      { id: 103, name: "Eucharistic Adoration", date: "Friday", time: "6:00 – 9:00 PM", category: "Adoration", description: "Holy Hour of silent prayer before the Blessed Sacrament.", recurring: true },
      { id: 104, name: "RCIA — Adult Faith Formation", date: "Wednesday", time: "7:00 PM", category: "Faith Formation", description: "Rite of Christian Initiation. Inquirers, candidates, and sponsors welcome.", recurring: true },
    ]
  },
  {
    id: 2, parish: "St. Ann Catholic Church", city: "West Palm Beach",
    events: [
      { id: 201, name: "Family Life Mass", date: "Sunday", time: "9:00 AM", category: "Mass", description: "Family-centered liturgy with children's Liturgy of the Word.", recurring: true },
      { id: 202, name: "Youth Ministry Night", date: "Thursday", time: "7:00 PM", category: "Youth", description: "High school and college-age young adults — games, prayer, and open discussion.", recurring: true },
      { id: 203, name: "St. Ann Food Pantry", date: "Saturday", time: "9:00 AM – 12:00 PM", category: "Service", description: "Community food distribution. Volunteers always gratefully accepted.", recurring: true },
      { id: 204, name: "Grief Support Group", date: "Monday", time: "6:30 PM", category: "Outreach", description: "A safe space to process grief through faith and shared community.", recurring: true },
    ]
  },
  {
    id: 3, parish: "St. Patrick Catholic Church", city: "Delray Beach",
    events: [
      { id: 301, name: "Spanish Mass", date: "Sunday", time: "1:00 PM", category: "Mass", description: "Misa solemne en español — todos son bienvenidos.", recurring: true },
      { id: 302, name: "Couples Retreat Weekend", date: "April 18–20", time: "Fri 6PM – Sun 3PM", category: "Retreat", description: "A Marriage Encounter–style retreat for couples seeking renewal and deeper connection.", recurring: false },
      { id: 303, name: "Men's Scripture Study", date: "Tuesday", time: "6:00 AM", category: "Faith Formation", description: "Early morning Bible study for men. Coffee and fellowship provided.", recurring: true },
      { id: 304, name: "Spring Gala & Fundraiser", date: "May 3", time: "6:00 PM", category: "Fundraiser", description: "Annual parish gala — dinner, live music, and a silent auction benefiting the school.", recurring: false },
    ]
  },
  {
    id: 4, parish: "Blessed Trinity Parish", city: "Boca Raton",
    events: [
      { id: 401, name: "Daily Morning Mass", date: "Weekdays", time: "7:00 AM", category: "Mass", description: "Monday through Friday morning Mass celebrated in the Lady Chapel.", recurring: true },
      { id: 402, name: "Children's Faith Formation", date: "Sunday", time: "10:15 AM", category: "Youth", description: "K–8 religious education classes during the 10AM Sunday Mass.", recurring: true },
      { id: 403, name: "Divine Mercy Chaplet", date: "Friday", time: "3:00 PM", category: "Adoration", description: "Communal praying of the Chaplet at the Hour of Mercy.", recurring: true },
      { id: 404, name: "Parish Picnic", date: "April 27", time: "12:00 PM", category: "Social", description: "Annual spring picnic for the whole parish family. Bring a dish to share!", recurring: false },
    ]
  },
];

const CATEGORIES = ["Mass","Confession","Adoration","Faith Formation","Youth","Service","Outreach","Retreat","Fundraiser","Social"];
const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Weekdays"];

const CAT = {
  "Mass":           { color: "#d4a853", glow: "rgba(212,168,83,0.18)" },
  "Confession":     { color: "#e07b54", glow: "rgba(224,123,84,0.18)" },
  "Adoration":      { color: "#7eb8d4", glow: "rgba(126,184,212,0.18)" },
  "Faith Formation":{ color: "#9b88d4", glow: "rgba(155,136,212,0.18)" },
  "Youth":          { color: "#d47eb8", glow: "rgba(212,126,184,0.18)" },
  "Service":        { color: "#7dd4a0", glow: "rgba(125,212,160,0.18)" },
  "Outreach":       { color: "#54b8a0", glow: "rgba(84,184,160,0.18)" },
  "Retreat":        { color: "#a0c878", glow: "rgba(160,200,120,0.18)" },
  "Fundraiser":     { color: "#d4c453", glow: "rgba(212,196,83,0.18)" },
  "Social":         { color: "#d48a7e", glow: "rgba(212,138,126,0.18)" },
};

const css = `
${GF}
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg0:#0d0d0f;
  --bg1:#121215;
  --bg2:#18181c;
  --bg3:#1e1e24;
  --bg4:#242430;
  --gold:#d4a853;
  --gold2:#b8882f;
  --text1:#f0ede6;
  --text2:#a09a90;
  --text3:#605a52;
  --border:#2a2a34;
  --border2:#38383f;
}
html,body{background:var(--bg0);color:var(--text1);font-family:'DM Sans',sans-serif}
.app{min-height:100vh;background:var(--bg0)}

.hero{
  position:relative;overflow:hidden;
  padding:4rem 2rem 3.5rem;text-align:center;
  background:radial-gradient(ellipse 60% 50% at 50% 0%,rgba(212,168,83,0.07) 0%,transparent 70%),var(--bg0);
}
.hero-lines{
  position:absolute;inset:0;
  background-image:linear-gradient(rgba(212,168,83,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(212,168,83,0.04) 1px,transparent 1px);
  background-size:60px 60px;
  mask-image:radial-gradient(ellipse 70% 60% at 50% 0%,black 0%,transparent 75%);
}
.hero-cross{font-size:1.2rem;color:var(--gold);letter-spacing:0.3em;margin-bottom:1.5rem;opacity:0.7;position:relative}
.hero-title{
  font-family:'Cormorant Garamond',serif;
  font-size:clamp(3rem,7vw,5.5rem);font-weight:300;
  letter-spacing:0.14em;color:var(--text1);text-transform:uppercase;line-height:1;position:relative;
}
.hero-title b{font-weight:700;color:var(--gold)}
.hero-rule{width:80px;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent);margin:1.5rem auto;position:relative}
.hero-sub{font-size:0.72rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--text2);position:relative}
.hero-stats{display:flex;justify-content:center;gap:3rem;margin-top:2.5rem;position:relative}
.stat-num{font-family:'Cormorant Garamond',serif;font-size:2.5rem;font-weight:600;color:var(--gold);display:block;line-height:1}
.stat-lbl{font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--text3);margin-top:4px;display:block}

.main{max-width:1120px;margin:0 auto;padding:2.5rem 1.5rem}

.sec-head{
  font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:400;
  color:var(--text1);letter-spacing:0.06em;margin-bottom:1.25rem;
  display:flex;align-items:center;gap:0.75rem;
}
.sec-head::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,var(--border2),transparent)}

.parser-card{
  background:var(--bg2);border:1px solid var(--border2);border-radius:16px;
  padding:1.75rem;margin-bottom:2.5rem;position:relative;overflow:hidden;
}
.parser-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--gold),transparent)}
.parser-label{font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:var(--gold);font-weight:500;margin-bottom:1rem}
.parser-row{display:flex;gap:0.75rem;flex-wrap:wrap;align-items:flex-start}
.p-select{
  background:var(--bg3);border:1px solid var(--border2);border-radius:10px;
  padding:0.65rem 1rem;font-family:'DM Sans',sans-serif;font-size:0.9rem;
  color:var(--text1);outline:none;min-width:200px;
}
.p-select:focus{border-color:var(--gold)}
.p-textarea{
  flex:1;min-width:220px;min-height:110px;
  background:var(--bg3);border:1px solid var(--border2);border-radius:10px;
  padding:0.85rem 1rem;font-family:'DM Sans',sans-serif;font-size:0.9rem;
  color:var(--text1);resize:vertical;outline:none;line-height:1.5;
}
.p-textarea::placeholder{color:var(--text3)}
.p-textarea:focus{border-color:var(--gold)}
.btn-parse{
  background:var(--gold);color:#0d0d0f;border:none;border-radius:10px;
  padding:0.75rem 1.5rem;font-family:'DM Sans',sans-serif;font-size:0.9rem;font-weight:600;
  cursor:pointer;white-space:nowrap;letter-spacing:0.02em;transition:background 0.2s,transform 0.1s;
}
.btn-parse:hover{background:#e8bc60}
.btn-parse:active{transform:scale(0.97)}
.btn-parse:disabled{background:var(--bg4);color:var(--text3);cursor:not-allowed}
.parse-note{font-size:0.76rem;color:var(--text3);margin-top:0.75rem}
.ai-msg{margin-top:1rem;padding:0.9rem 1.1rem;border-radius:10px;font-size:0.86rem;border-left:3px solid}
.ai-msg.ok{background:rgba(125,212,160,0.08);border-color:#7dd4a0;color:#7dd4a0}
.ai-msg.err{background:rgba(224,123,84,0.08);border-color:#e07b54;color:#e07b54}

.search-row{display:flex;gap:0.65rem;margin-bottom:1rem;flex-wrap:wrap}
.s-input{
  flex:1;min-width:220px;background:var(--bg2);border:1px solid var(--border2);
  border-radius:10px;padding:0.7rem 1.1rem;font-family:'DM Sans',sans-serif;font-size:0.95rem;
  color:var(--text1);outline:none;transition:border-color 0.2s;
}
.s-input::placeholder{color:var(--text3)}
.s-input:focus{border-color:var(--gold)}
.f-select{
  background:var(--bg2);border:1px solid var(--border2);border-radius:10px;
  padding:0.65rem 1rem;font-family:'DM Sans',sans-serif;font-size:0.88rem;color:var(--text2);outline:none;cursor:pointer;
}
.f-select:focus{border-color:var(--gold)}

.pill-row{display:flex;gap:0.4rem;flex-wrap:wrap;margin-bottom:1.5rem}
.pill{
  border-radius:20px;padding:0.3rem 0.9rem;font-size:0.76rem;font-weight:500;
  cursor:pointer;border:1px solid var(--border2);background:var(--bg2);color:var(--text2);
  transition:all 0.15s;letter-spacing:0.03em;white-space:nowrap;
}
.pill:hover{color:var(--text1);border-color:var(--border)}
.pill.on{background:var(--gold);color:#0d0d0f;border-color:var(--gold);font-weight:600}

.res-count{font-size:0.76rem;color:var(--text3);margin-bottom:1.5rem;letter-spacing:0.05em}

.parish-block{margin-bottom:2.75rem}
.parish-hdr{
  display:flex;align-items:center;gap:0.9rem;
  margin-bottom:1.1rem;padding-bottom:0.75rem;border-bottom:1px solid var(--border);
}
.parish-ico{
  width:40px;height:40px;border-radius:50%;
  background:var(--bg3);border:1px solid var(--border2);
  display:flex;align-items:center;justify-content:center;
  font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:700;color:var(--gold);flex-shrink:0;
}
.parish-nm{font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:600;color:var(--text1)}
.parish-city{font-size:0.75rem;color:var(--text3);margin-top:2px;letter-spacing:0.04em}
.parish-count{margin-left:auto;font-size:0.72rem;color:var(--text3);letter-spacing:0.05em}

.evt-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1rem}
.evt-card{
  background:var(--bg2);border:1px solid var(--border);border-radius:14px;
  padding:1.15rem 1.25rem;cursor:pointer;position:relative;overflow:hidden;
  transition:border-color 0.2s,transform 0.2s,box-shadow 0.2s;
}
.evt-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,var(--c,transparent) 0%,transparent 60%);opacity:0.5;
}
.evt-card:hover{border-color:var(--c,var(--border2));transform:translateY(-3px);box-shadow:0 8px 30px var(--glow,rgba(0,0,0,0.3))}
.evt-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem}
.evt-name{font-size:0.96rem;font-weight:500;color:var(--text1);line-height:1.3;flex:1;margin-right:0.5rem}
.evt-badge{
  font-size:0.66rem;font-weight:600;letter-spacing:0.06em;
  padding:0.2rem 0.6rem;border-radius:20px;border:1px solid;white-space:nowrap;flex-shrink:0;
}
.evt-when{font-size:0.81rem;color:var(--text2);margin-bottom:0.4rem}
.evt-when b{color:var(--c,var(--gold))}
.evt-desc{font-size:0.79rem;color:var(--text3);line-height:1.5}
.recur{
  display:inline-flex;align-items:center;gap:4px;margin-top:0.6rem;
  font-size:0.66rem;font-weight:500;color:var(--text3);letter-spacing:0.06em;text-transform:uppercase;
}
.recur-dot{width:5px;height:5px;border-radius:50%;background:var(--c,var(--gold));opacity:0.7}

.empty{text-align:center;padding:4rem 1rem;color:var(--text3)}
.empty-cross{font-family:'Cormorant Garamond',serif;font-size:3rem;color:var(--border2);margin-bottom:1rem}
.empty h3{font-family:'Cormorant Garamond',serif;font-size:1.3rem;color:var(--text2);margin-bottom:0.4rem}
.empty p{font-size:0.84rem}

.overlay{
  position:fixed;inset:0;background:rgba(0,0,0,0.75);
  backdrop-filter:blur(6px);display:flex;align-items:center;
  justify-content:center;z-index:9999;padding:1.5rem;
}
.modal{
  background:var(--bg2);border:1px solid var(--border2);border-radius:20px;
  padding:2rem;max-width:480px;width:100%;position:relative;
  box-shadow:0 30px 80px rgba(0,0,0,0.7);overflow:hidden;
}
.modal::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--mc,var(--gold)),transparent);
}
.m-close{
  position:absolute;top:1.1rem;right:1.1rem;
  background:var(--bg3);border:1px solid var(--border);border-radius:8px;
  width:30px;height:30px;cursor:pointer;color:var(--text2);font-size:0.85rem;
  display:flex;align-items:center;justify-content:center;
}
.m-close:hover{background:var(--bg4);color:var(--text1)}
.m-badge{
  font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
  padding:0.25rem 0.75rem;border-radius:20px;border:1px solid;display:inline-block;margin-bottom:1rem;
}
.m-title{font-family:'Cormorant Garamond',serif;font-size:1.75rem;font-weight:600;color:var(--text1);line-height:1.2;margin-bottom:0.25rem}
.m-parish{font-size:0.82rem;color:var(--mc,var(--gold));font-weight:500;letter-spacing:0.04em;margin-bottom:1.25rem}
.m-row{display:flex;gap:0.75rem;align-items:flex-start;padding:0.65rem 0;border-top:1px solid var(--border)}
.m-ico{font-size:0.9rem;width:20px;flex-shrink:0;margin-top:1px}
.m-key{font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text3);margin-bottom:2px}
.m-val{font-size:0.88rem;color:var(--text2)}
.m-desc{margin-top:1rem;padding:1rem;background:var(--bg3);border-radius:10px;font-size:0.86rem;color:var(--text2);line-height:1.55;border:1px solid var(--border)}
.btn-share{
  width:100%;margin-top:1.25rem;background:transparent;
  border:1px solid var(--mc,var(--gold));border-radius:10px;padding:0.8rem;
  font-family:'DM Sans',sans-serif;font-size:0.86rem;font-weight:500;
  color:var(--mc,var(--gold));cursor:pointer;letter-spacing:0.08em;text-transform:uppercase;
  transition:background 0.2s,color 0.2s;
}
.btn-share:hover{background:var(--mc,var(--gold));color:#0d0d0f}

.footer{
  text-align:center;padding:2.5rem 1rem;
  font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;
  color:var(--text3);border-top:1px solid var(--border);margin-top:2rem;
}
.footer-cross{color:var(--gold);margin:0 0.6rem}
`;

export default function App() {
  const [data, setData] = useState(SAMPLE_DATA);
  const [search, setSearch] = useState("");
  const [fParish, setFParish] = useState("All");
  const [fDay, setFDay] = useState("Any");
  const [fCat, setFCat] = useState("All");
  const [sel, setSel] = useState(null);
  const [bText, setBText] = useState("");
  const [bParish, setBParish] = useState("1");
  const [parsing, setParsing] = useState(false);
  const [parseRes, setParseRes] = useState(null);

  const totalEvts = data.reduce((s, p) => s + p.events.length, 0);

  const filtered = data
    .filter(p => fParish === "All" || p.id.toString() === fParish)
    .map(p => ({
      ...p,
      events: p.events.filter(e => {
        const q = search.toLowerCase();
        return (!q || [e.name, e.description, e.category].join(" ").toLowerCase().includes(q))
          && (fDay === "Any" || e.date.toLowerCase().includes(fDay.toLowerCase()))
          && (fCat === "All" || e.category === fCat);
      })
    }))
    .filter(p => p.events.length > 0);

  const totalFiltered = filtered.reduce((s, p) => s + p.events.length, 0);

  const parse = async () => {
    if (!bText.trim()) return;
    setParsing(true); setParseRes(null);
    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{ role: "user", content: `You are a parish bulletin parser for a Catholic diocese. Extract all events from the bulletin text and return ONLY a JSON array (no markdown). Each event: name, date, time, category (one of: Mass, Confession, Adoration, Faith Formation, Youth, Service, Outreach, Retreat, Fundraiser, Social), description (1 sentence), recurring (boolean). If no events, return [].\n\nBulletin:\n"""\n${bText}\n"""` }]
        })
      });
      const json = await res.json();
      const txt = json.content?.map(b => b.text || "").join("") || "[]";
      const events = JSON.parse(txt.replace(/```json|```/g, "").trim());
      if (!Array.isArray(events) || !events.length) {
        setParseRes({ ok: false, msg: "No events detected. Paste more complete bulletin content." });
        return;
      }
      const stamped = events.map((e, i) => ({ ...e, id: Date.now() + i }));
      setData(prev => prev.map(p => p.id.toString() === bParish ? { ...p, events: [...p.events, ...stamped] } : p));
      const pName = data.find(p => p.id.toString() === bParish)?.parish;
      setParseRes({ ok: true, count: events.length, parish: pName });
      setBText("");
    } catch {
      setParseRes({ ok: false, msg: "Parse failed. Check the bulletin text and try again." });
    } finally { setParsing(false); }
  };

  const initials = name => name.split(" ").filter(w => /^[A-Z]/.test(w)).slice(0,2).map(w=>w[0]).join("");

  return (
    <>
      <style>{css}</style>
      <div className="app">

        <div className="hero">
          <div className="hero-lines" />
          <div className="hero-cross">✦ ✝ ✦</div>
          <h1 className="hero-title">COMMU<b>NIO</b></h1>
          <div className="hero-rule" />
          <p className="hero-sub">Diocese of Palm Beach · Parish Event Directory</p>
          <div className="hero-stats">
            <div><span className="stat-num">{data.length}</span><span className="stat-lbl">Parishes</span></div>
            <div><span className="stat-num">{totalEvts}</span><span className="stat-lbl">Events</span></div>
            <div><span className="stat-num" style={{fontSize:"1.5rem",paddingTop:"6px"}}>AI</span><span className="stat-lbl">Powered</span></div>
          </div>
        </div>

        <div className="main">

          <h2 className="sec-head">Bulletin Parser</h2>
          <div className="parser-card">
            <p className="parser-label">✦ AI Event Import — Paste any parish bulletin or newsletter below</p>
            <div className="parser-row">
              <select className="p-select" value={bParish} onChange={e => setBParish(e.target.value)}>
                {data.map(p => <option key={p.id} value={p.id}>{p.parish}</option>)}
              </select>
              <textarea className="p-textarea" value={bText} onChange={e => setBText(e.target.value)}
                placeholder="Paste the full text of a parish bulletin or weekly newsletter. The AI will extract all events, dates, times, and categories automatically…" />
              <button className="btn-parse" onClick={parse} disabled={parsing || !bText.trim()}>
                {parsing ? "Parsing…" : "⚡ Parse Events"}
              </button>
            </div>
            <p className="parse-note">Events are automatically categorized and added to the live directory. Works with any bulletin format.</p>
            {parseRes && (
              <div className={`ai-msg ${parseRes.ok ? "ok" : "err"}`}>
                {parseRes.ok ? `✓ ${parseRes.count} event${parseRes.count > 1 ? "s" : ""} added from ${parseRes.parish}` : `⚠ ${parseRes.msg}`}
              </div>
            )}
          </div>

          <h2 className="sec-head">Find Events</h2>
          <div className="search-row">
            <input className="s-input" type="text" placeholder="Search by name, description, or keyword…"
              value={search} onChange={e => setSearch(e.target.value)} />
            <select className="f-select" value={fParish} onChange={e => setFParish(e.target.value)}>
              <option value="All">All Parishes</option>
              {data.map(p => <option key={p.id} value={p.id}>{p.parish}</option>)}
            </select>
            <select className="f-select" value={fDay} onChange={e => setFDay(e.target.value)}>
              <option value="Any">Any Day</option>
              {DAYS.map(d => <option key={d}>{d}</option>)}
            </select>
          </div>

          <div className="pill-row">
            <button className={`pill ${fCat === "All" ? "on" : ""}`} onClick={() => setFCat("All")}>All</button>
            {CATEGORIES.map(cat => {
              const color = CAT[cat]?.color || "#d4a853";
              const active = fCat === cat;
              return (
                <button key={cat} className="pill"
                  style={active
                    ? { borderColor: color, color, background: color + "18" }
                    : {}}
                  onClick={() => setFCat(fCat === cat ? "All" : cat)}>{cat}</button>
              );
            })}
          </div>

          <p className="res-count">
            {totalFiltered} event{totalFiltered !== 1 ? "s" : ""}{" "}
            {(search || fCat !== "All" || fDay !== "Any" || fParish !== "All") ? "matching current filters" : "in the directory"}
          </p>

          {filtered.length === 0 ? (
            <div className="empty">
              <div className="empty-cross">✝</div>
              <h3>No events found</h3>
              <p>Try broadening your search, or parse a new bulletin above.</p>
            </div>
          ) : filtered.map(parish => (
            <div key={parish.id} className="parish-block">
              <div className="parish-hdr">
                <div className="parish-ico">{initials(parish.parish)}</div>
                <div>
                  <div className="parish-nm">{parish.parish}</div>
                  <div className="parish-city">📍 {parish.city}</div>
                </div>
                <span className="parish-count">{parish.events.length} event{parish.events.length !== 1 ? "s" : ""}</span>
              </div>
              <div className="evt-grid">
                {parish.events.map(evt => {
                  const cs = CAT[evt.category] || { color: "#d4a853", glow: "rgba(212,168,83,0.15)" };
                  return (
                    <div key={evt.id} className="evt-card"
                      style={{ "--c": cs.color, "--glow": cs.glow }}
                      onClick={() => setSel({ ...evt, parishName: parish.parish, parishCity: parish.city })}>
                      <div className="evt-top">
                        <div className="evt-name">{evt.name}</div>
                        <span className="evt-badge" style={{ borderColor: cs.color + "44", color: cs.color }}>{evt.category}</span>
                      </div>
                      <div className="evt-when"><b>{evt.date}</b>{evt.time ? ` · ${evt.time}` : ""}</div>
                      <div className="evt-desc">{evt.description}</div>
                      {evt.recurring && <div className="recur"><span className="recur-dot" />Recurring</div>}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {sel && (() => {
          const cs = CAT[sel.category] || { color: "#d4a853" };
          return (
            <div className="overlay" onClick={() => setSel(null)}>
              <div className="modal" style={{ "--mc": cs.color }} onClick={e => e.stopPropagation()}>
                <button className="m-close" onClick={() => setSel(null)}>✕</button>
                <span className="m-badge" style={{ borderColor: cs.color + "55", color: cs.color }}>{sel.category}</span>
                <h2 className="m-title">{sel.name}</h2>
                <p className="m-parish">✝ {sel.parishName}</p>
                <div className="m-row">
                  <span className="m-ico">📅</span>
                  <div><div className="m-key">Date</div><div className="m-val">{sel.date}</div></div>
                </div>
                <div className="m-row">
                  <span className="m-ico">🕐</span>
                  <div><div className="m-key">Time</div><div className="m-val">{sel.time || "See parish for times"}</div></div>
                </div>
                <div className="m-row">
                  <span className="m-ico">📍</span>
                  <div><div className="m-key">Location</div><div className="m-val">{sel.parishCity}</div></div>
                </div>
                {sel.recurring && (
                  <div className="m-row">
                    <span className="m-ico">↻</span>
                    <div><div className="m-key">Frequency</div><div className="m-val">Recurring weekly event</div></div>
                  </div>
                )}
                <div className="m-desc">{sel.description}</div>
                <button className="btn-share" onClick={() => {
                  const t = `${sel.name} — ${sel.parishName} · ${sel.date}${sel.time ? " at " + sel.time : ""}`;
                  if (navigator.share) navigator.share({ title: sel.name, text: t });
                  else { navigator.clipboard.writeText(t); alert("Copied to clipboard!"); }
                }}>Share This Event</button>
              </div>
            </div>
          );
        })()}

        <div className="footer">
          <span className="footer-cross">✦</span>
          Communio · Diocese of Palm Beach · {new Date().getFullYear()}
          <span className="footer-cross">✦</span>
        </div>
      </div>
    </>
  );
}
