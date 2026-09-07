import React, { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
    };
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught component error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleReset = () => {
    this.setState({ hasError: false });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen w-full bg-[#0A0A0A] text-white flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 rounded-3xl bg-[#ff334b]/20 border-2 border-[#ff334b] flex items-center justify-center mb-5 text-[#ff334b] shadow-[0_0_30px_rgba(255,51,75,0.4)]">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h1 className="text-xl font-black tracking-tight text-white mb-2">
            PULSEGRID EMERGENCY RECOVERY
          </h1>
          <p className="text-xs text-[#AAAAAA] max-w-sm mb-6 leading-relaxed">
            The emergency visual interface recovered from an unexpected rendering pause. Tap below
            to restore live hospital telemetry.
          </p>
          <div className="flex gap-3">
            <button
              onClick={this.handleReset}
              className="px-5 py-2.5 rounded-full bg-[#E2FF4D] text-black font-black text-xs uppercase tracking-wider hover:brightness-110 active:scale-95 transition-all shadow-lg cursor-pointer"
            >
              Resume Telemetry
            </button>
            <button
              onClick={this.handleReload}
              className="px-4 py-2.5 rounded-full bg-[#1A1A1A] border border-[#333333] text-white font-bold text-xs flex items-center gap-1.5 hover:border-[#E2FF4D] transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reload
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
