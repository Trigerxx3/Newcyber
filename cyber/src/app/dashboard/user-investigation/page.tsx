import { UserInvestigationDashboard } from '@/components/user-investigation-dashboard';

export default function UserInvestigationPage() {
    return (
        <main className="flex-1 p-4 sm:p-6 md:p-8">
            <div className="max-w-screen-2xl mx-auto">
                <UserInvestigationDashboard />
            </div>
        </main>
    );
}
