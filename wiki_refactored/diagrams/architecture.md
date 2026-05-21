```mermaid
flowchart TD
    %% Main Application
    subgraph Main[Main Application]
        main[main()] --> fetch_data[Fetch Data]
        main --> process_data[Process Data]
        main --> visualize[Visualize]
        main --> display_ui[Display UI]
    end
    
    %% Data Fetching Functions
    subgraph Fetch[Data Fetching]
        get_fred[get_fred_series(series_id)]
        get_stable[get_stablecoin_marketcap()]
        get_etf[get_etf_data(symbol, name)]
        fetch_all[fetch_all_etf_data()]
    end
    
    %% Data Processing Functions
    subgraph Process[Data Processing]
        build_master[build_master_dataframe()]
    end
    
    %% Visualization Functions
    subgraph Viz[Visualization]
        axis_style[create_axis_style()]
        line_chart[create_line_chart(data, x, y, ...)]
        dual_chart[create_dual_line_chart(data, id_vars, value_vars, ...)]
    end
    
    %% Connections
    main --> get_fred
    main --> get_stable
    main --> get_etf
    main --> fetch_all
    main --> build_master
    main --> axis_style
    main --> line_chart
    main --> dual_chart
    
    %% Data flow
    get_fred --> build_master
    get_stable --> build_master
    get_etf --> build_master
    fetch_all --> build_master
    build_master --> line_chart
    build_master --> dual_chart
    
    %% Styling
    classDef main fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef fetch fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef process fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px;
    classDef viz fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;
    
    class main Main;
    class fetch Fetch;
    class process Process;
    class viz Viz;

```