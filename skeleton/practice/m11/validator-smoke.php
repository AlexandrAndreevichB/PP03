<?php

declare(strict_types=1);

require __DIR__ . '/../../src/Validator.php';

$cases = [
    ['valid', 'reader@example.test', false],
    ['empty', '', true],
    ['invalid format', 'reader', true],
];
$failed = false;

foreach ($cases as [$name, $value, $shouldFail]) {
    $validator = new Validator(['email' => $value]);
    $validator->required('email')->email('email');
    $matches = $validator->fails() === $shouldFail;
    $failed = $failed || !$matches;
    printf("%s %s\n", $matches ? 'PASS' : 'FAIL', $name);
}

exit($failed ? 1 : 0);
