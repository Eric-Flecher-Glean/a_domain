// Test the highlightXML function
function highlightXML(xml) {
  return xml
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(&lt;\\/?)?([\\w-]+)/g, '<span class="xml-tag">$1$2</span>')
    .replace(/([\\w-]+)(=)/g, '<span class="xml-attr">$1</span>$2')
    .replace(/="([^"]*)"/g, '="<span class="xml-value">$1</span>"');
}

const testXML = `<metadata>
  <name>jt1-zin-kkz</name>
</metadata>`;

console.log('INPUT:', testXML);
console.log('\nOUTPUT:', highlightXML(testXML));
