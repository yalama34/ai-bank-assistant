export interface LetterResponse {
  original_letter: string;
  generated_response: string;
  validation_score: number;
  validation_result: {
    score: number;
    auto_send_eligible: boolean;
    issues?: string[];
    recommendations?: string[];
  };
  processing_params: Record<string, any>;
  request_category: string | null;
  auto_send_eligible: boolean;
}
