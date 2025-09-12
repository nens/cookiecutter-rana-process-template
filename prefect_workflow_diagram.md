# Prefect Workflow Diagram for Rana Process Template

```mermaid
graph TD
    A[Input: ProcessInputs] --> B["@rana_flow Decorator"]
    B --> C[Validate Call Signature]
    C --> D[Create Prefect Flow]
    D --> E[Flow Execution Start]
    
    E --> F[RanaContext Setup]
    F --> G[Context Manager __enter__]
    G --> H[Create Working Directory]
    H --> I[Setup Logger]
    I --> J[Create Progress Artifact]
    
    J --> K["Process Function: process()"]
    K --> L["Set Progress: 0%"]
    L --> M["Set Progress: 50%"]
    M --> N[Process Input: inputs.name]
    N --> O[Transform: name.upper()]
    O --> P[Set Output: ProcessOutputs]
    
    P --> Q[Output Validation]
    Q --> R[File Upload/Download Operations]
    R --> S[Set Result Artifact]
    
    S --> T[Context Manager __exit__]
    T --> U[Cleanup Working Directory]
    U --> V[Remove ThreeDi API Key]
    V --> W["Set Progress: 100%"]
    W --> X[Flow Completion]

    %% Context Components
    subgraph "Context Types"
        F1[PrefectRanaContext]
        F2[LocalTestRanaContext]
    end
    
    %% Runtime Components
    subgraph "Runtime Components"
        R1[PrefectRanaRuntime]
        R2[LocalTestRanaRuntime]
        R3[Gateways]
    end
    
    %% Gateways and External Services
    subgraph "Gateways & Services"
        G1[RanaFileGateway]
        G2[RanaDatasetGateway]
        G3[RanaSchematisationGateway]
        G4[LizardRasterLayerGateway]
        G5[ThreediApiKeyGateway]
    end
    
    %% Error Handling
    subgraph "Error Handling"
        E1[ProcessUserError]
        E2[ProcessInternalError]
        E3[Exception Logging]
    end
    
    %% Flow Control
    F --> F1
    F1 --> R1
    R1 --> R3
    R3 --> G1
    R3 --> G2
    R3 --> G3
    R3 --> G4
    R3 --> G5
    
    %% Error Flow
    K -.->|Exception| E3
    E3 --> E1
    E3 --> E2
    
    %% Local Test Flow
    F -.->|Local Testing| F2
    F2 --> R2

    %% Styling
    classDef processNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef contextNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef runtimeNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef gatewayNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef errorNode fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,K,P processNode
    class F,F1,F2 contextNode
    class R1,R2,R3 runtimeNode
    class G1,G2,G3,G4,G5 gatewayNode
    class E1,E2,E3 errorNode
```

## Workflow Components Description

### Core Flow
1. **Input Processing**: Starts with `ProcessInputs` containing user parameters
2. **Flow Decoration**: `@rana_flow` decorator wraps the process function with Prefect functionality
3. **Context Setup**: Initializes the appropriate runtime context (Prefect or Local Test)
4. **Process Execution**: Runs the main process logic with progress tracking
5. **Output Handling**: Validates and uploads output files to Rana platform
6. **Cleanup**: Removes temporary resources and finalizes the workflow

### Runtime Contexts
- **PrefectRanaContext**: Production runtime for Prefect-based execution
- **LocalTestRanaContext**: Development runtime for local testing

### Gateways & External Services
- **RanaFileGateway**: Handles file upload/download operations
- **RanaDatasetGateway**: Manages dataset operations
- **RanaSchematisationGateway**: Handles 3Di schematisation files
- **LizardRasterLayerGateway**: Interfaces with Lizard raster services
- **ThreediApiKeyGateway**: Manages 3Di API authentication

### Error Handling
- **ProcessUserError**: User-facing errors with formatted messages
- **ProcessInternalError**: Internal system errors
- Comprehensive exception logging and progress tracking
