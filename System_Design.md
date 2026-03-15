flowchart TB
    subgraph A[Inner Loop - What exists today]
        A1[deploy.sh] --> A2[autofix.sh]
        A2 --> A3[Build]
        A3 --> A4[Flash]
        A4 --> A5[test_runner.py UART verify]
        A5 --> A6[Logs and reports]
    end

    subgraph B[Outer Agent - What we are building]
        B1[User request] --> B2[Load state and lessons]
        B2 --> B3[Create TaskSpec]
        B3 --> B4[Create isolated workspace]
        B4 --> B5[Invoke coding agent]
        B5 --> B6[Guardrails]
        B6 --> B7[Call inner loop]
        B7 --> B8[Evaluate result]
        B8 --> B9[Promote verified baseline]
        B9 --> B10[Update persistent state]
    end

    B7 --> A1