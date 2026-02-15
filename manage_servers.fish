#!/usr/bin/env fish

# AutoFinance MCP Server Manager
# Start/Stop HTTP proxy for MCP servers

set BASE_DIR ~/Documents/AutoFinance
set VENV_PYTHON $BASE_DIR/venv/bin/python
set PROXY_SCRIPT $BASE_DIR/mcp_http_proxy.py
set PID_FILE /tmp/autofinance_proxy.pid

function start_proxy
    echo "🚀 Starting AutoFinance MCP HTTP Proxy..."
    
    # Check if already running
    if test -f $PID_FILE
        set old_pid (cat $PID_FILE)
        if ps -p $old_pid > /dev/null 2>&1
            echo "⚠️  Proxy already running (PID: $old_pid)"
            echo "   Stop it first with: ./manage_servers.fish stop"
            return 1
        end
    end
    
    # Start proxy in background
    $VENV_PYTHON $PROXY_SCRIPT > /tmp/autofinance_proxy.log 2>&1 &
    set proxy_pid $last_pid
    echo $proxy_pid > $PID_FILE
    
    # Wait a moment and verify
    sleep 2
    
    if ps -p $proxy_pid > /dev/null 2>&1
        echo "✅ Proxy running (PID: $proxy_pid)"
        echo ""
        echo "🌐 Server URLs:"
        echo "   http://localhost:9100/market"
        echo "   http://localhost:9100/risk"
        echo "   http://localhost:9100/execution"
        echo "   http://localhost:9100/compliance"
        echo "   http://localhost:9100/technical"
        echo ""
        echo "📝 Logs: tail -f /tmp/autofinance_proxy.log"
    else
        echo "❌ Failed to start proxy"
        echo "   Check logs: cat /tmp/autofinance_proxy.log"
        return 1
    end
end

function stop_proxy
    echo "🛑 Stopping AutoFinance MCP HTTP Proxy..."
    
    if test -f $PID_FILE
        set proxy_pid (cat $PID_FILE)
        
        if ps -p $proxy_pid > /dev/null 2>&1
            kill $proxy_pid
            echo "✅ Stopped proxy (PID: $proxy_pid)"
        else
            echo "⚠️  Proxy not running"
        end
        
        rm -f $PID_FILE
    else
        echo "⚠️  No PID file found"
    end
end

function status_proxy
    echo "📊 AutoFinance MCP Proxy Status"
    echo "================================"
    
    if test -f $PID_FILE
        set proxy_pid (cat $PID_FILE)
        
        if ps -p $proxy_pid > /dev/null 2>&1
            echo "Status: ✅ RUNNING"
            echo "PID: $proxy_pid"
            echo ""
            echo "Test with:"
            echo "  curl http://localhost:9100/servers"
        else
            echo "Status: ❌ NOT RUNNING (stale PID file)"
            rm -f $PID_FILE
        end
    else
        echo "Status: ❌ NOT RUNNING"
    end
end

# Main script
if test (count $argv) -eq 0
    echo "Usage: ./manage_servers.fish [start|stop|restart|status]"
    echo ""
    echo "Commands:"
    echo "  start   - Start HTTP proxy"
    echo "  stop    - Stop HTTP proxy"
    echo "  restart - Restart HTTP proxy"
    echo "  status  - Check proxy status"
    exit 1
end

switch $argv[1]
    case start
        start_proxy
    case stop
        stop_proxy
    case restart
        stop_proxy
        sleep 1
        start_proxy
    case status
        status_proxy
    case '*'
        echo "Unknown command: $argv[1]"
        echo "Use: start, stop, restart, or status"
        exit 1
end
