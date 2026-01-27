// Debug script for timeline modal issue
// Copy and paste this into browser console (Cmd+Opt+J)

console.log('🔍 Starting Modal Debug...\n');

// Step 1: Check if TIMELINE_DATA exists
console.log('Step 1: TIMELINE_DATA Check');
if (typeof TIMELINE_DATA === 'undefined') {
  console.error('❌ TIMELINE_DATA is not defined!');
} else {
  console.log('✅ TIMELINE_DATA exists');
  console.log('   Rows:', TIMELINE_DATA.rows.length);
  console.log('   Has outputContent:', !!TIMELINE_DATA.outputContent);
}

// Step 2: Check if blocks exist
console.log('\nStep 2: Duration Blocks Check');
const blocks = document.querySelectorAll('.duration-block');
console.log(`Found ${blocks.length} blocks with class "duration-block"`);

if (blocks.length === 0) {
  console.error('❌ No .duration-block elements found!');
  console.log('Checking for SVG...');
  const svg = document.querySelector('svg');
  if (svg) {
    console.log('✅ SVG exists');
    const rects = svg.querySelectorAll('rect');
    console.log(`   Found ${rects.length} rect elements in SVG`);
    if (rects.length > 0) {
      console.log('   First rect classes:', rects[0].className.baseVal);
    }
  } else {
    console.error('❌ No SVG element found!');
  }
} else {
  console.log('✅ Blocks found');
  blocks.forEach((block, i) => {
    console.log(`   Block ${i + 1}: ${block.getAttribute('data-row-name')}`);
    console.log(`      - spanId: ${block.getAttribute('data-span-id')}`);
    console.log(`      - pointer-events: ${window.getComputedStyle(block).pointerEvents}`);
    console.log(`      - cursor: ${window.getComputedStyle(block).cursor}`);
  });
}

// Step 3: Check if modal element exists
console.log('\nStep 3: Modal Element Check');
const modal = document.getElementById('spanModal');
if (!modal) {
  console.error('❌ Modal element #spanModal not found!');
} else {
  console.log('✅ Modal element exists');
  console.log('   Current display:', window.getComputedStyle(modal).display);
  console.log('   Current classes:', modal.className);
  console.log('   Position:', window.getComputedStyle(modal).position);
  console.log('   Z-index:', window.getComputedStyle(modal).zIndex);
}

// Step 4: Check if functions exist
console.log('\nStep 4: Function Check');
const functions = ['openModal', 'closeModal', 'showModalContent', 'switchTab', 'highlightXML', 'copyToClipboard'];
functions.forEach(fn => {
  if (typeof window[fn] === 'function') {
    console.log(`✅ ${fn}() exists`);
  } else {
    console.error(`❌ ${fn}() not found!`);
  }
});

// Step 5: Test click manually
console.log('\nStep 5: Manual Click Test');
if (blocks.length > 0) {
  console.log('Attempting to click first block programmatically...');

  const testBlock = blocks[0];
  const blockName = testBlock.getAttribute('data-row-name');

  console.log(`Target: ${blockName}`);

  // Check if event listener is attached
  const listenerCount = getEventListeners ? getEventListeners(testBlock).click?.length : 'unknown';
  console.log('Click listeners attached:', listenerCount);

  // Trigger click
  console.log('Clicking now...');
  testBlock.click();

  setTimeout(() => {
    console.log('\nChecking modal state after click:');
    const modalNow = document.getElementById('spanModal');
    console.log('   Has .active class:', modalNow.classList.contains('active'));
    console.log('   Style.display:', modalNow.style.display);
    console.log('   Computed display:', window.getComputedStyle(modalNow).display);

    if (modalNow.classList.contains('active') || modalNow.style.display === 'flex') {
      console.log('✅ Modal appears to be open!');

      // Check if it's visible
      const rect = modalNow.getBoundingClientRect();
      console.log('   Modal position:', rect);
      console.log('   Modal visibility:', window.getComputedStyle(modalNow).visibility);
      console.log('   Modal opacity:', window.getComputedStyle(modalNow).opacity);

      // Close it
      closeModal();
      console.log('   Closed modal for you');
    } else {
      console.error('❌ Modal did NOT open');
      console.log('\nPossible issues:');
      console.log('   1. Check browser console for JavaScript errors (red text)');
      console.log('   2. Event listener may not be attached');
      console.log('   3. Click handler may be throwing an error');
    }
  }, 1000);
} else {
  console.error('❌ No blocks to test!');
}

console.log('\n🔍 Debug complete. Check results above.\n');
