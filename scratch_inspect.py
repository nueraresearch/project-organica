import sys, json
sys.path.insert(0, r'C:\Users\monte\anti\project-organica')
from organica.memory import MemoryService
from organica.sleep import SleepService

m = MemoryService()

events = [
    ('function called with arguments', 'event'),
    ('test passed after code modification', 'event'),
    ('auth failure on login attempt', 'event'),
    ('session expired triggering re-auth', 'event'),
    ('build pipeline triggered on push', 'event'),
    ('tests passed all suites green', 'event'),
    ('deployment succeeded to staging', 'event'),
    ('auth session renewed successfully', 'event'),
    ('pull request merged into main branch', 'event'),
    ('code review approved by reviewer', 'event'),
    ('test failed due to assertion error', 'event'),
    ('hotfix branch created for critical bug', 'event'),
    ('issue reported in production system', 'event'),
    ('fix committed to feature branch', 'event'),
    ('issue closed after verification', 'event'),
    ('resource consumed by organism', 'event'),
    ('organism reproduced successfully', 'event'),
    ('predator prey interaction observed', 'event'),
    ('sensor reading acquired from environment', 'event'),
    ('action planned based on sensor data', 'event'),
    ('goal reached after navigation sequence', 'event'),
]
for text, etype in events:
    m.store(text, event_type=etype, source='inspect')

s = SleepService(m)
r = s.run_sleep_cycle()

print('=== CONCEPTS ===')
for c in r.concepts:
    print(' ', c.members, 'conf:', round(c.confidence, 3))

print()
print('=== PREDICTIONS (top 10) ===')
for p in r.predictions[:10]:
    print('  {} -> {}  strength:{}'.format(p.source, p.target, round(p.strength, 3)))

print()
print('=== LOOPS ===')
for lp in r.loops[:5]:
    print(' ', ' -> '.join(lp.path), 'strength:', round(lp.strength, 3))

print()
print('=== HYPOTHESES ===')
for h in r.hypotheses:
    print('  [{}] subject={!r} expects={!r} conf={} support={} contradictions={}'.format(
        h.id, h.subject, h.expectation, round(h.confidence, 3), h.support_count, h.contradiction_count))

print()
print('=== DREAMS ===')
for d in r.dreams:
    print('  [{}] subject={!r} path={} novelty={}'.format(
        d.dream_category, d.subject, d.path_or_context, round(d.novelty, 3)))

print()
print('=== INVESTIGATIONS ===')
for i in r.investigations:
    eig = getattr(i, 'eig', getattr(i, 'expected_information_gain', 0))
    rationale = getattr(i, 'rationale', getattr(i, 'source_question_id', ''))
    subj = getattr(i, 'target_subject', getattr(i, 'subject', '?'))
    print('  [{}] target={!r} eig={} rationale={}'.format(
        i.id, subj, round(float(eig), 3), rationale))

print()
print('=== EXPERIMENTS ===')
for e in r.experiments:
    anchor = getattr(e, 'injected_anchor', getattr(e, 'anchor', '?'))
    cat = getattr(e, 'dream_category', getattr(e, 'category', '?'))
    orig = getattr(e, 'original_components', getattr(e, 'components', []))
    print('  anchor={!r} dream_cat={!r} original={}'.format(anchor, cat, orig))
