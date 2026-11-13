"""Kiểm tra từng tính năng mới bằng mô phỏng: python3 tools/featuretest.py"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['low'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]; R={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000)
        pg.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
        pg.on('console', lambda m: errs.append('console: '+m.text) if m.type=='error' and '404' not in m.text else None)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        ev=pg.evaluate
        async def gwait(sec):
            t0=await ev("window.__game.state.time"); await pg.wait_for_function(f"window.__game.state.time>{t0}+{sec}", timeout=400000)
        await ev("(async()=>{ const g=window.__game; g.settings.map='khesanh'; g.settings.mode='base'; await g.startCampaign(); })()")
        await pg.wait_for_function("window.__game.state.phase==='playing'")
        # 1) hạ địch -> có tiền trên xác -> chạy tới nhặt
        R['loot']=await ev("""(async()=>{ const g=window.__game, e=g.enemies[0]; const m0=g.state.money; g.damageEnemy(e,9999,true,null); const loot=e.loot; g.player.pos.set(e.pos.x+0.5,0,e.pos.z); await new Promise(r=>setTimeout(r,1500)); return {loot, gained:g.state.money-m0, kVN:g.state.kVN}; })()""")
        # 2) đồng đội gục -> cứu bằng E
        await ev("""(()=>{ const g=window.__game, a=g.allies[4]; g.damageUnit(a,9999,null); g.player.pos.set(a.pos.x+0.8,0,a.pos.z); window.__ra=a; })()""")
        await pg.keyboard.down('e'); await gwait(2.6); await pg.keyboard.up('e')
        R['revive']=await ev("(()=>{ const a=window.__ra; return {alive:a.alive, down:!!a.down, meds:window.__game.player.meds}; })()")
        # 3) bộc phá vào xe chỉ huy địch
        R['charge']=await ev("""(async()=>{ const g=window.__game, h=g.hqs.find(h=>h.side==='en'); const hp0=h.hp; g.plantCharge(new g.V3(h.x0-0.6,0.1,h.z), 'p'); g.player.pos.set(h.x0-30,0,h.z); g.player.invuln=99; window.__hp0=hp0; })()""")
        await gwait(6); R['charge']=await ev("(()=>{ const h=window.__game.hqs.find(h=>h.side==='en'); return {hp0:window.__hp0, hp:Math.round(h.hp)}; })()")
        # 4) chiếm pháo
        R['art']=await ev("""(async()=>{ const g=window.__game; const a=g.arts.find(a=>!a.gunner)||g.arts[0]; if(!a) return 'no art'; a.gunner=null; g.player.pos.set(a.x+2.1,0,a.z); return 'ok'; })()""")
        await pg.keyboard.down('e'); await gwait(1.2); await pg.keyboard.up('e')
        R['art_mounted']=await ev("!!window.__game.player.onArt")
        await ev("window.__game.player.fireHeld=true"); await gwait(1.0); await ev("window.__game.player.fireHeld=false")
        await pg.screenshot(path=f'{shots}/feat_art.png')
        await pg.keyboard.press('e'); await pg.wait_for_timeout(500); R['art_left']=await ev("!window.__game.player.onArt")
        # 5) tiếp tế: thả và nhặt
        await ev("window.__game.supplyDrop()"); await gwait(16)
        R['supply']=await ev("""(async()=>{ const g=window.__game; const c=g.crates.find(c=>c.side==='vn'&&c.alive); if(!c) return {crates:g.crates.length}; const ar=g.player.armor; g.player.pos.set(c.x,0,c.z); const t0=g.state.time; while(g.state.time<t0+0.5) await new Promise(r=>setTimeout(r,200)); return {landed:c.landed, taken:!c.alive, armor:g.player.armor, nades:g.player.nades}; })()""")
        await pg.screenshot(path=f'{shots}/feat_supply.png')
        # 6) chết -> hồi sinh sau 8s
        await ev("(()=>{ const g=window.__game; g.player.invuln=0; g.player.armor=0; g.player.hp=5; g.plantCharge(new g.V3(g.player.pos.x+0.5,0.1,g.player.pos.z),'e'); })()")
        await gwait(5.6); R['dead']=await ev("!window.__game.player.alive")
        await pg.screenshot(path=f'{shots}/feat_dead.png')
        await gwait(8.5); R['respawned']=await ev("window.__game.player.alive")
        # 7) chiếm lô cốt
        await ev("(async()=>{ const g=window.__game; g.settings.map='himlam'; await g.startCampaign(); })()")
        await pg.wait_for_function("window.__game.state.phase==='playing' && window.__game.state.mission==='bunker'")
        R['bunker']=await ev("""(async()=>{ const g=window.__game, c=g.capCells[0]; for(const e of g.enemies){ if(e.alive && Math.hypot(e.pos.x-c.x,e.pos.z-c.z)<10) g.damageEnemy(e,9999,false,null,true); } g.player.pos.set(c.x,0,c.z); g.player.invuln=99; })()""")
        for _ in range(4):
            await ev("(()=>{ const g=window.__game, c=g.capCells[0]; for(const e of g.enemies){ if(e.alive && Math.hypot(e.pos.x-c.x,e.pos.z-c.z)<7) g.damageEnemy(e,9999,false,null,true); } g.player.pos.set(c.x,0,c.z); })()"); await gwait(3.5)
        R['bunker']=await ev("(()=>{ const g=window.__game; return {capIdx:g.state.capIdx, prog:g.state.capProg, tickets:g.state.tickets}; })()")
        await pg.screenshot(path=f'{shots}/feat_bunker.png')
        await b.close()
    return errs, R
check.prep(); pr=check.server()
try:
    errs,R=asyncio.run(run()); print(json.dumps({'errors':errs[:20],'report':R},ensure_ascii=False,indent=1)); print('KẾT QUẢ:', 'ĐẠT' if not errs else 'CÓ LỖI')
finally: pr.terminate()
