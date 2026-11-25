<?php

declare(strict_types=1);

$projectRoot = $argv[1] ?? '';
$helperPath = $projectRoot . '/src/helpers.php';
if ($projectRoot === '' || !is_file($helperPath)) {
    fwrite(STDERR, "Usage: php characterization-plural.php <kait-library root>\n");
    exit(2);
}

require $helperPath;

$cases = [
    0 => 'дней',
    1 => 'день',
    2 => 'дня',
    5 => 'дней',
    11 => 'дней',
    21 => 'день',
];
$failures = 0;
foreach ($cases as $count => $expected) {
    $actual = plural($count, 'день', 'дня', 'дней');
    $matches = $actual === $expected;
    $failures += (int)!$matches;
    printf("%s n=%d expected=%s actual=%s\n", $matches ? 'PASS' : 'FAIL', $count, $expected, $actual);
}

exit($failures === 0 ? 0 : 1);
