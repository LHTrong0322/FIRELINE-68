"""Chụp ảnh đại diện cho từng bản đồ (sảnh online): python3 tools/thumbs.py"""
import asyncio, os, sys
sys.argv=[sys.argv[0],'high']
import check
from PIL import Image
async def run():
    from playwright.async_api import async_playwright
    out=f'{check.ROOT}/public/assets/maps'; os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':800,'height':450}); await ctx.add_init_script("try{localStorage.setItem('tl_quality3', JSON.stringify('high'))}catch(e){}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        ids=await pg.evaluate("Object.keys(window.__game.MAPS)")
        for mid in ids:
            await pg.evaluate(f"(async()=>{{ const g=window.__game; g.settings.map='{mid}'; g.settings.mode='rescue'; await g.startCampaign(); }})()")
            await pg.wait_for_function("window.__game.state.phase==='playing'")
            await pg.add_style_tag(content="#hud{display:none!important} #touch{display:none!important}")
            await pg.evaluate("""(()=>{ const g=window.__game, P=g.player, W=g.MAPS[g.MAPID]; const cols=W.grid[0].length, rows=W.grid.length;
                for(const e of g.enemies){ e.react=999; e.cool=999; } for(const a of g.allies) a.model.group.visible=false; for(const h of g.hostages) h.model.group.visible=false; g.player.invuln=999; if(W.outdoor) g.applyEnvMix(0);
                const out=!!W.outdoor; const c=P.pos; const tx=cols*g.CELL/2, tz=rows*g.CELL/2; const yaw=Math.atan2(-(tx-c.x), -(tz-c.z));
                window.__camOverride = out ? {p:[c.x, 9, c.z], r:[-0.32, yaw]} : {p:[c.x,1.6,c.z], r:[-0.03, yaw]};
                g.state.phase='thumb'; })()""")
            await pg.wait_for_timeout(9000)
            f=f'/tmp/thumb_{mid}.png'; await pg.screenshot(path=f)
            Image.open(f).convert('RGB').resize((400,225),Image.LANCZOS).save(f'{out}/{mid}.jpg',quality=82)
            print('thumb', mid)
        await b.close()
check.prep(); pr=check.server()
try: asyncio.run(run())
finally: pr.terminate()
