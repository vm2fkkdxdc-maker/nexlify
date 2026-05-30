const intakeForm = document.getElementById('intake-form');
const scenarioResults = document.getElementById('scenario-results');
const policyFeed = document.getElementById('policy-feed');
const buildPolicyFeedBtn = document.getElementById('build-policy-feed');
const exportMemoBtn = document.getElementById('export-memo');
const exportStatus = document.getElementById('export-status');

let latestScenarioSet = [];

function getScenarioScores(budget, riskTolerance) {
  const budgetFactor = Math.max(0, Math.min(20, budget / 10));
  const riskAdjustments = {
    low: { certainty: 10, upside: -8, speed: -3 },
    balanced: { certainty: 4, upside: 3, speed: 2 },
    high: { certainty: -4, upside: 12, speed: 4 }
  };
  const adjustment = riskAdjustments[riskTolerance] || riskAdjustments.balanced;

  const scenarios = [
    {
      name: 'Public-First Blend',
      stack: 'TIF + grant + municipal debt + private equity',
      certainty: 65 + adjustment.certainty + budgetFactor,
      upside: 58 + adjustment.upside,
      speed: 62 + adjustment.speed,
      risk: 'Lower financing volatility, slower approvals.'
    },
    {
      name: 'Balanced Partnership Stack',
      stack: 'Tax credits + infrastructure support + sponsor debt',
      certainty: 61 + adjustment.certainty,
      upside: 69 + adjustment.upside + budgetFactor / 2,
      speed: 68 + adjustment.speed,
      risk: 'Balanced risk with moderate policy dependency.'
    },
    {
      name: 'Private-Led Acceleration',
      stack: 'Sponsor equity + bridge debt + targeted incentives',
      certainty: 50 + adjustment.certainty,
      upside: 79 + adjustment.upside,
      speed: 76 + adjustment.speed,
      risk: 'Faster delivery with higher downside sensitivity.'
    }
  ];

  scenarios.forEach((s) => {
    s.total = Math.round((s.certainty * 0.4) + (s.upside * 0.35) + (s.speed * 0.25));
  });

  return scenarios.sort((a, b) => b.total - a.total);
}

function renderScenarios(scenarios) {
  scenarioResults.innerHTML = '';

  scenarios.forEach((scenario, index) => {
    const item = document.createElement('div');
    item.className = 'scenario';
    item.innerHTML = `
      <p><strong>#${index + 1} ${scenario.name}</strong></p>
      <p>Stack: ${scenario.stack}</p>
      <p>Total score: ${scenario.total} | Certainty: ${Math.round(scenario.certainty)} | Upside: ${Math.round(scenario.upside)} | Speed: ${Math.round(scenario.speed)}</p>
      <p>Tradeoff: ${scenario.risk}</p>
    `;
    scenarioResults.appendChild(item);
  });
}

function buildPolicyTimeline(startDateValue) {
  policyFeed.innerHTML = '';
  if (!startDateValue) {
    const li = document.createElement('li');
    li.textContent = 'Select a start date to map policy and regulatory milestones.';
    policyFeed.appendChild(li);
    return;
  }

  const startDate = new Date(startDateValue);
  const milestones = [
    { weeks: 2, label: 'Agency pre-application alignment' },
    { weeks: 6, label: 'Incentive package review and legal validation' },
    { weeks: 10, label: 'Public hearing and stakeholder commitments' },
    { weeks: 14, label: 'Regulatory clearance and contracting' },
    { weeks: 18, label: 'Execution kickoff and accountability reporting' }
  ];

  milestones.forEach((milestone) => {
    const target = new Date(startDate);
    target.setDate(startDate.getDate() + (milestone.weeks * 7));

    const li = document.createElement('li');
    li.textContent = `${target.toISOString().split('T')[0]} — ${milestone.label}`;
    policyFeed.appendChild(li);
  });
}

function exportDecisionMemo() {
  const projectName = document.getElementById('project-name').value.trim() || 'Untitled Project';
  const budget = document.getElementById('budget').value;
  const riskTolerance = document.getElementById('risk-tolerance').value;
  const stakeholders = document.getElementById('stakeholders').value.trim();
  const timelineItems = Array.from(policyFeed.querySelectorAll('li')).map((li) => `- ${li.textContent}`);
  const checklistItems = Array.from(document.querySelectorAll('#execution-checklist li')).map((li) => {
    const checked = li.querySelector('input').checked ? '[x]' : '[ ]';
    return `- ${checked} ${li.textContent.replace(/\s+/g, ' ').trim()}`;
  });

  const scenarioText = latestScenarioSet.length
    ? latestScenarioSet.map((s, i) => `${i + 1}. ${s.name} (${s.total}) | ${s.stack} | ${s.risk}`).join('\n')
    : 'No scenarios generated yet.';

  const memo = `Clutch Decision Memo\n\nProject: ${projectName}\nBudget ($M): ${budget || 'N/A'}\nRisk tolerance: ${riskTolerance}\nStakeholders: ${stakeholders || 'N/A'}\n\nScenario ranking:\n${scenarioText}\n\nPolicy milestone timeline:\n${timelineItems.length ? timelineItems.join('\n') : '- Timeline not generated'}\n\nExecution checklist:\n${checklistItems.join('\n')}\n\nDisclaimer: Clutch outputs are informational and operational planning support only, and are not legal, tax, investment, or financial advice.`;

  const blob = new Blob([memo], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${projectName.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'clutch'}-decision-memo.txt`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);

  exportStatus.textContent = 'Decision memo exported.';
}

if (intakeForm) {
  intakeForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const budget = Number(document.getElementById('budget').value);
    const riskTolerance = document.getElementById('risk-tolerance').value;
    latestScenarioSet = getScenarioScores(budget, riskTolerance);
    renderScenarios(latestScenarioSet);
  });
}

if (buildPolicyFeedBtn) {
  buildPolicyFeedBtn.addEventListener('click', () => {
    const dateValue = document.getElementById('start-date').value;
    buildPolicyTimeline(dateValue);
  });
}

if (exportMemoBtn) {
  exportMemoBtn.addEventListener('click', exportDecisionMemo);
}
