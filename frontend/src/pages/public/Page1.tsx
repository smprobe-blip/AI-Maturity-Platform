import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { useAuditStore } from '@/store/auditStore';
import { INDUSTRIES, COMPANY_SIZES, REGIONS } from '@/utils/constants';

const schema = z.object({
  industry: z.string().min(1, 'Выберите отрасль'),
  company_size: z.string().min(1, 'Выберите размер компании'),
  region: z.string().min(1, 'Выберите регион'),
  email: z.string().email('Некорректный email'),
  name: z.string().optional(),
  position: z.string().optional(),
  consent: z.literal(true, {
    errorMap: () => ({ message: 'Необходимо согласие на обработку данных' }),
  }),
});

type FormData = z.infer<typeof schema>;

export default function Page1() {
  const navigate = useNavigate();
  const { setCompanyProfile, setContactInfo } = useAuditStore();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    setCompanyProfile({
      industry: data.industry,
      company_size: data.company_size,
      region: data.region,
    });

    setContactInfo({
      email: data.email,
      name: data.name,
      position: data.position,
      consent_to_process_data: data.consent,
    });

    navigate('/assessment');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Оценка ИИ-зрелости
          </h1>
          <p className="text-lg text-gray-600">
            Узнайте уровень зрелости вашей компании в области искусственного интеллекта
          </p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="Отрасль"
                error={errors.industry?.message}
                options={INDUSTRIES.map((i) => ({ value: i, label: i }))}
                {...register('industry')}
              />

              <Select
                label="Размер компании"
                error={errors.company_size?.message}
                options={COMPANY_SIZES.map((s) => ({ value: s, label: s }))}
                {...register('company_size')}
              />
            </div>

            <Select
              label="Регион"
              error={errors.region?.message}
              options={REGIONS.map((r) => ({ value: r, label: r }))}
              {...register('region')}
            />

            <Input
              label="Email"
              type="email"
              placeholder="your@company.com"
              error={errors.email?.message}
              {...register('email')}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Имя"
                placeholder="Иван Иванов"
                error={errors.name?.message}
                {...register('name')}
              />

              <Input
                label="Должность"
                placeholder="CTO, Director..."
                error={errors.position?.message}
                {...register('position')}
              />
            </div>

            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="consent"
                className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                {...register('consent')}
              />
              <label htmlFor="consent" className="text-sm text-gray-700">
                Я согласен на обработку персональных данных в соответствии с 152-ФЗ
                {errors.consent && (
                  <p className="text-danger-500 text-xs mt-1">{errors.consent.message}</p>
                )}
              </label>
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Загрузка...' : 'Начать оценку →'}
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          ⏱️ Время прохождения: ~5 минут • 📊 35 вопросов по 7 осям
        </p>
      </div>
    </div>
  );
}