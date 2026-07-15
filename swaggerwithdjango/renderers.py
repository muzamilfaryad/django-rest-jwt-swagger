from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def _flatten_errors(self, data):
        if isinstance(data, dict):
            already_exists_fields = []
            other_messages = []

            for field, errors in data.items():
                msgs = errors if isinstance(errors, list) else [errors]
                for msg in msgs:
                    if "already exists" in str(msg).lower():
                        already_exists_fields.append(field)
                    else:
                        other_messages.append(f"{field}: {msg}")

            messages = []
            if len(already_exists_fields) > 1:
                fields_str = " and ".join(already_exists_fields)
                messages.append(f"A user with this {fields_str} already exists.")
            elif len(already_exists_fields) == 1:
                messages.append(f"A user with this {already_exists_fields[0]} already exists.")

            messages.extend(other_messages)
            return " ".join(messages)

        elif isinstance(data, list):
            return " ".join(str(item) for item in data)
        elif isinstance(data, str):
            return data
        return ""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            view = renderer_context.get('view')
            if view and view.__class__.__name__ in ['SpectacularAPIView', 'SpectacularSwaggerView', 'SpectacularRedocView']:
                return super().render(data, accepted_media_type, renderer_context)

            response = renderer_context.get('response')
            status_code = response.status_code if response else 200
        else:
            status_code = 200

        if isinstance(data, dict) and 'status' in data and 'message' in data and 'data' in data:
            return super().render(data, accepted_media_type, renderer_context)

        is_success = 200 <= status_code < 300

        custom_message = None
        if response:
            custom_message = response.get('X-Message')

        response_dict = {
            "status": "success" if is_success else "error",
            "message": custom_message if custom_message else ("Request processed successfully." if is_success else "An error occurred."),
            "data": data if is_success else None
        }

        if not is_success:
            if isinstance(data, dict):
                if 'detail' in data:
                    response_dict['message'] = str(data['detail'])
                else:
                    response_dict['message'] = self._flatten_errors(data)
            elif isinstance(data, list):
                response_dict['message'] = self._flatten_errors(data)
            elif isinstance(data, str):
                response_dict['message'] = data

        return super().render(response_dict, accepted_media_type, renderer_context)
