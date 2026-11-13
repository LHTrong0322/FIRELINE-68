"""Chụp chân dung nhân vật trong game (soi mặt/da/mắt): python3 tools/portrait.py [high]"""
import asyncio, os, sys
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['high'])
import check
async def run():
    from playwright.async_api import async_playwright
    shots=f'{check.ROOT}/tools/shots'; errs=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':960,'height':540}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.set_default_timeout(300000); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        await pg.evaluate("(async()=>{ const g=window.__game; g.settings.map='" + (os.environ.get('MAP') or 'khesanh') + "'; g.settings.mode='base'; await g.startCampaign(); g.player.invuln=9999; })()")
        await pg.wait_for_timeout(5000)
        for i,(side,dist) in enumerate([('vn',0.95),('us',0.95),('vn',2.6)]):
            await pg.evaluate(f"""(()=>{{ const g=window.__game,p=g.player; p.yaw=Math.atan2(-0.555,-0.377)+Math.PI; p.pitch=-0.03;
              const fx=-Math.sin(p.yaw), fz=-Math.cos(p.yaw);
              const list = '{side}'==='vn' ? g.allies : g.enemies; if('{side}'==='us' && !g.enemies.length) g.spawnEnemy('rifle');
              const L=('{side}'==='vn'?g.allies:g.enemies); g.allies.concat(g.enemies).forEach(u=>{{ if(u.model&&u.model.group) u.model.group.visible=false; }});
              const u=L[0]; u.model.group.visible=true; u.pos.set(p.pos.x+fx*{dist}, 0, p.pos.z+fz*{dist}); u.yaw=p.yaw; u.cool=99; u.react=99; u.state='guard'; u.goal=null;
              document.getElementById('hud').style.visibility='hidden'; }})()""")
            await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{shots}/portrait_{i}.png')
        await b.close()
    return errs
check.prep(); pr=check.server()
try: print('errors', asyncio.run(run()))
finally: pr.terminate()
