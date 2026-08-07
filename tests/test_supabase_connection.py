from app.services.supabase_service import SupabaseService


service = SupabaseService()

if service.test_connection():
    print("Supabase connection successful.")
else:
    print("Supabase connection failed.")