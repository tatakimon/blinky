==========================================================================================
==========================================================================================


Layer 1 — firmware workspace


    This is the actual STM32 project that gets edited, built, flashed, and verified.

    Main files:

    Dell_2_Steval/

    especially Dell_2_Steval/Core/Src/main.c

    This is the thing being changed.

==========================================================================================

==========================================================================================

Layer 2 — primitive agent / execution engine


    This is your first real product.

    It already exists in primitive form.

    Main files:

    deploy.sh

    autofix.sh

    test_runner.py

    These are the files that run the closed loop:

    receive task

    call Codex

    build

    flash

    UART verify

    write logs

    This is your first product.

==========================================================================================
==========================================================================================


Layer 3 — full firmware agent

    This is the bigger system you want later.

    It will sit on top of Layer 2.

    It will do things like:

    accept user request

    load memory/state

    create TaskSpec

    create isolated workspace

    decide approval

    manage LKG

    commit/promote verified versions

    store lessons/failures

    support Telegram or other interfaces

    This is your final product direction.

==========================================================================================
==========================================================================================
