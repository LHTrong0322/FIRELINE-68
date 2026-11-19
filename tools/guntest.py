"""Chụp súng góc nhìn thứ nhất (AK, RPD, B40) ở tư thế thường và ngắm, ban ngày Khe Sanh.
Chạy: python3 tools/guntest.py [low|high]  -> tools/shots/gun_<id>_<hip|ads>.png"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check
Q=sys.argv[1] if len(sys.argv)>1 else 'high'; check.Q=Q
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; os.makedirs(shots, exist_ok=True); errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(240000)
        pg.on('pageerror', lambda e: errs.append('pageerror: '+str(e)))
        pg.on('console', lambda m: errs.append('console: '+m.text) if m.type=='error' and '404' not in m.text else None)
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("(async()=>{ const g=window.__game; g.settings.map='khesanh'; g.settings.mode='base'; await g.startCampaign(); g.state.waveT=999; })()")
        await pg.wait_for_function("window.__game.state.phase==='playing'", timeout=300000)
        await pg.wait_for_timeout(2500)
        await pg.evaluate("(()=>{const g=window.__game; g.state.money=999999; g.shopBuy('rpd'); g.shopClose&&g.shopClose(); g.player.pitch=-0.12;})()")
        for idx,name in [x for x in ((4,'rpd'),(2,'ak'),(3,'b40')) if x[1] in os.environ.get('GUNS','rpd,ak,b40')]:
            await pg.evaluate(f"(()=>{{const g=window.__game; g.switchWeapon({idx}); g.player.swap=0; g.player.aimHeld=false;}})()")
            await pg.wait_for_function("window.__game.player.ads<0.02 && window.__game.player.swap<=0", timeout=120000)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{shots}/gun_{name}_hip.png')
            await pg.evaluate("window.__game.player.aimHeld=true")
            await pg.wait_for_function("window.__game.player.ads>0.98", timeout=120000)
            await pg.wait_for_timeout(800); await pg.screenshot(path=f'{shots}/gun_{name}_ads.png')
            await pg.evaluate("window.__game.player.aimHeld=false")
        await b.close()
    return errs
if __name__=='__main__':
    check.prep(); pr=check.server()
    try: errs=asyncio.run(run())
    finally: pr.terminate()
    print(json.dumps({'quality':Q,'errors':errs[:20]}, ensure_ascii=False)); sys.exit(1 if errs else 0)
