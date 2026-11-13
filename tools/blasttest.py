"""Kiểm tra sát thương nổ pháo: địch đứng sau bao cát/hào gần điểm nổ phải chết: python3 tools/blasttest.py"""
import asyncio, os, sys, json
sys.argv=[sys.argv[0]]+(sys.argv[1:] or ['low'])
import check
async def run():
    from playwright.async_api import async_playwright
    errs=[]; rep={}
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        ctx=await b.new_context(viewport={'width':640,'height':360}); await ctx.add_init_script(f"try{{localStorage.setItem('tl_quality4', JSON.stringify('{check.Q}'))}}catch(e){{}}")
        pg=await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8799/'); await pg.wait_for_function('window.__gameReady===true', timeout=300000)
        for mp in ['khesanh','himlam']:
            await pg.evaluate(f"(async()=>{{ const g=window.__game; g.settings.map='{mp}'; g.settings.mode='base'; await g.startCampaign(); g.player.invuln=9999; }})()")
            await pg.wait_for_function("window.__game.state.phase==='playing'", timeout=200000)
            rep[mp]=await pg.evaluate("""(()=>{ const g=window.__game; let killed=0, n=0;
              for(const e of g.enemies.slice(0,8)){ if(!e.alive) continue; n++; const a=Math.random()*6.28, r=2+Math.random()*3; g.explode(new g.V3(e.pos.x+Math.cos(a)*r,0.2,e.pos.z+Math.sin(a)*r),'p',{R:8,dmg:280}); if(!e.alive) killed++; }
              return {n, killed}; })()""")
        await b.close()
    return errs, rep
check.prep(); pr=check.server()
try: errs,rep=asyncio.run(run())
finally: pr.terminate()
ok = not errs and all(v['n']>0 and v['killed']>=v['n']*0.7 for v in rep.values())
print(json.dumps({'errors':errs,'report':rep},ensure_ascii=False)); print('KẾT QUẢ:', 'ĐẠT' if ok else 'CÓ LỖI')
